INSERT INTO `USER_ROLE` (user_id, role_id, created_at)
SELECT u.id, r.id, NOW()
FROM `USER` u
JOIN `ROLE` r ON r.code='USER'
LEFT JOIN `USER_ROLE` ur ON ur.user_id = u.id AND ur.role_id = r.id
WHERE ur.user_id IS NULL;


ALTER TABLE `USER_ROLE`
  MODIFY `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP;
COMMIT;