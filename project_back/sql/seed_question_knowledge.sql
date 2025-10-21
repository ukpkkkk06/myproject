-- ========================================
-- 填充 QUESTION_KNOWLEDGE 表
-- ========================================
-- 用途: 为题目关联知识点,支持智能推荐功能
-- 创建时间: 2025-10-21
-- 更新时间: 2025-10-21
-- ========================================

USE myexam_db;

-- 清空现有数据(如果有)
TRUNCATE TABLE QUESTION_KNOWLEDGE;


-- ========================================
-- 权重设计原则
-- ========================================
-- weight 字段表示"题目与知识点的关联强度" (0-100):
--   100 = 该知识点是题目的主要考点(直接关联)
--   60  = 该知识点是宽泛相关的父节点(继承关联)
--
-- 层级优先原则:
--   - 层级越深的知识点,权重应该越高
--   - 当题目同时关联父子知识点时:
--     * 子节点(更具体) → weight=100 (优先推荐)
--     * 父节点(更宽泛) → weight=60  (次要推荐)
--
-- 推荐逻辑示例:
--   用户在"四则运算"(level=1)出错时:
--     1. 优先推荐: weight=100 的题目(直接考察四则运算)
--     2. 次要推荐: 通过父节点"数学"继承的题目
-- ========================================

-- ========================================
-- 第一步: 建立基础关联 (权重=100)
-- ========================================

-- 1. 单选题(SC)关联到"数学"知识点
INSERT INTO QUESTION_KNOWLEDGE (question_id, knowledge_id, weight)
SELECT 
    q.id,
    1 as knowledge_id, -- 数学 (level=0)
    100 as weight  -- 主要考点
FROM QUESTION q
WHERE q.is_active = 1 
  AND q.type = 'SC';

-- 2. 简单单选题同时关联到"四则运算"知识点(更深层级)
INSERT INTO QUESTION_KNOWLEDGE (question_id, knowledge_id, weight)
SELECT 
    q.id,
    2 as knowledge_id, -- 四则运算 (level=1)
    100 as weight  -- 主要考点(更具体)
FROM QUESTION q
WHERE q.is_active = 1 
  AND q.type = 'SC'
  AND q.difficulty <= 2;

-- 3. 多选题(MC)关联到"英语"知识点
INSERT INTO QUESTION_KNOWLEDGE (question_id, knowledge_id, weight)
SELECT 
    q.id,
    3 as knowledge_id, -- 英语 (level=0)
    100 as weight
FROM QUESTION q
WHERE q.is_active = 1 
  AND q.type = 'MC';

-- 4. 填空题(FILL)关联到"物理"知识点
INSERT INTO QUESTION_KNOWLEDGE (question_id, knowledge_id, weight)
SELECT 
    q.id,
    5 as knowledge_id, -- 物理 (level=0)
    100 as weight
FROM QUESTION q
WHERE q.is_active = 1 
  AND q.type = 'FILL';

-- ========================================
-- 第二步: 调整父节点权重 (层级优先原则)
-- ========================================

-- 对于同时关联"数学"和"四则运算"的题目:
--   - "四则运算"(level=1, 更深) → weight=100 (保持)
--   - "数学"(level=0, 父节点) → weight=60 (降低,表示宽泛关联)
UPDATE QUESTION_KNOWLEDGE
SET weight = 60
WHERE knowledge_id = 1  -- 数学
  AND question_id IN (
    SELECT question_id FROM (
      SELECT question_id FROM QUESTION_KNOWLEDGE WHERE knowledge_id = 2
    ) as temp
  );

-- ========================================
-- 第三步: 处理其他题型(如果有)
-- ========================================

-- 5. 其他题型默认分配到"数学"
INSERT INTO QUESTION_KNOWLEDGE (question_id, knowledge_id, weight)
SELECT 
    q.id,
    1 as knowledge_id, -- 数学
    70 as weight
FROM QUESTION q
WHERE q.is_active = 1 
  AND q.type NOT IN ('SC', 'MC', 'FILL')
  AND NOT EXISTS (
      SELECT 1 FROM QUESTION_KNOWLEDGE qk WHERE qk.question_id = q.id
  );

-- ========================================
-- 验证数据
-- ========================================

-- 1. 基础统计
SELECT 
    COUNT(*) as 总记录数,
    COUNT(DISTINCT question_id) as 关联题目数,
    COUNT(DISTINCT knowledge_id) as 关联知识点数
FROM QUESTION_KNOWLEDGE;

-- 2. 按知识点查看分布(验证层级权重设计)
SELECT 
    kp.name as 知识点名称,
    kp.level as 层级,
    COUNT(qk.id) as 关联题目数,
    MIN(qk.weight) as 最小权重,
    MAX(qk.weight) as 最大权重,
    ROUND(AVG(qk.weight), 2) as 平均权重,
    GROUP_CONCAT(DISTINCT qk.weight ORDER BY qk.weight) as 权重分布
FROM QUESTION_KNOWLEDGE qk
JOIN KNOWLEDGE_POINT kp ON qk.knowledge_id = kp.id
GROUP BY kp.id, kp.name, kp.level
ORDER BY kp.level, COUNT(qk.id) DESC;

-- 3. 按题型查看分布
SELECT 
    q.type as 题型,
    kp.name as 知识点,
    COUNT(*) as 题目数量,
    ROUND(AVG(qk.weight), 2) as 平均权重
FROM QUESTION_KNOWLEDGE qk
JOIN QUESTION q ON qk.question_id = q.id
JOIN KNOWLEDGE_POINT kp ON qk.knowledge_id = kp.id
WHERE q.is_active = 1
GROUP BY q.type, kp.name
ORDER BY q.type, kp.name;

-- 4. 验证层级优先原则(查看同时关联父子节点的题目)
SELECT 
    q.id as 题目ID,
    q.type as 题型,
    GROUP_CONCAT(
        CONCAT(kp.name, '(层级', kp.level, ',权重', qk.weight, ')')
        ORDER BY kp.level DESC
        SEPARATOR ' + '
    ) as 关联知识点,
    CASE 
        WHEN MAX(CASE WHEN kp.level = 1 THEN qk.weight END) = 100 
         AND MAX(CASE WHEN kp.level = 0 THEN qk.weight END) = 60
        THEN '✓ 符合层级优先原则'
        ELSE '需检查'
    END as 权重验证
FROM QUESTION q
JOIN QUESTION_KNOWLEDGE qk ON q.id = qk.question_id
JOIN KNOWLEDGE_POINT kp ON qk.knowledge_id = kp.id
WHERE q.is_active = 1
GROUP BY q.id, q.type
HAVING COUNT(DISTINCT kp.level) > 1  -- 只看关联了多个层级的题目
ORDER BY q.id
LIMIT 10;

-- ========================================
-- 预期结果
-- ========================================
-- 总记录数: 77
-- 关联题目数: 70 (100%覆盖率)
-- 关联知识点数: 4
--
-- 知识点分布:
--   数学(level=0): 59题, 权重60-100, 平均95.3 (7题weight=60, 52题weight=100)
--   四则运算(level=1): 7题, 权重100 (深层优先)
--   英语(level=0): 6题, 权重100
--   物理(level=0): 5题, 权重100
--
-- 层级优先验证:
--   7道题同时关联"数学"(weight=60)和"四则运算"(weight=100)
--   符合"层级越深,权重越高"的设计原则
-- ========================================
