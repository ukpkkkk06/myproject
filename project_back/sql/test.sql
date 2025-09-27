INSERT INTO `USER_ROLE` (user_id, role_id, created_at)
SELECT u.id, r.id, NOW()
FROM `USER` u
JOIN `ROLE` r ON r.code='USER'
LEFT JOIN `USER_ROLE` ur ON ur.user_id = u.id AND ur.role_id = r.id
WHERE ur.user_id IS NULL;


ALTER TABLE `USER_ROLE`
  MODIFY `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP;

  INSERT INTO `TAG` (`name`,`type`,`is_active`) VALUES
('数学','SUBJECT',1),('物理','SUBJECT',1),('化学','SUBJECT',1),('英语','SUBJECT',1),('语文','SUBJECT',1)
ON DUPLICATE KEY UPDATE type=VALUES(type), is_active=VALUES(is_active);


INSERT INTO `TAG` (`name`,`type`,`is_active`) VALUES
('小学','LEVEL',1),('初中','LEVEL',1),('高中','LEVEL',1),('大学','LEVEL',1)
ON DUPLICATE KEY UPDATE type=VALUES(type), is_active=VALUES(is_active);

COMMIT;