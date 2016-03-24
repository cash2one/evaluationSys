CREATE TABLE `strategy_version` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `version_code` bigint(11) NOT NULL DEFAULT 0 COMMENT '版本号',
  `version_name` varchar(512) NOT NULL DEFAULT '' COMMENT '版本名称',
  `version_desc` varchar(512) NOT NULL DEFAULT '' COMMENT '版本描述',
  `git_branch` varchar(32) NOT NULL DEFAULT 'master' COMMENT 'git branch',
  `git_commit_id` varchar(64) NOT NULL DEFAULT '' COMMENT 'git commit id',
  `feature_version` bigint(11) NOT NULL DEFAULT 0 COMMENT '特征版本',
  `sample_version` bigint(11) NOT NULL DEFAULT 0 COMMENT '样本版本',
  `action_version` bigint(11) NOT NULL DEFAULT 0 COMMENT '用户行为库版本',
  `ctime` bigint(11) NOT NULL DEFAULT 0 COMMENT '版本创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `version` (`version_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='策略版本信息表'
