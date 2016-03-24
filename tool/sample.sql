CREATE TABLE `sample` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `cuid` char(64) NOT NULL DEFAULT '' COMMENT 'cuid',
  `sample_type` tinyint(4) NOT NULL DEFAULT 0 COMMENT '0正样本,1负样本',
  `ctime` bigint(11) NOT NULL DEFAULT 0 COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `cuid` (`cuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='样本库'
