CREATE TABLE `data_version` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `data_type` tinyint(4) NOT NULL DEFAULT 0 COMMENT '数据类型（1特征数据，2用户行为数据，）',
  `version_code` bigint(11) NOT NULL DEFAULT 0 COMMENT '版本号',
  `version_name` varchar(512) NOT NULL DEFAULT '' COMMENT '版本名称',
  `version_desc` varchar(512) NOT NULL DEFAULT '' COMMENT '版本描述',
  `file_path` varchar(512) NOT NULL DEFAULT '' COMMENT '文件路径（路径＋filename）',
  `ctime` bigint(11) NOT NULL DEFAULT 0 COMMENT '版本创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `version` (`version_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='数据版本信息表'
