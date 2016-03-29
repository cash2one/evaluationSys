CREATE TABLE `jobpool` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `strategy_code` bigint(11) NOT NULL DEFAULT 0 COMMENT '策略版本号',
  `ctime` bigint(11) NOT NULL DEFAULT 0 COMMENT '版本创建时间',
  `mtime` bigint(11) NOT NULL DEFAULT 0 COMMENT '最后更新时间',
  `job_status` tinyint(4) NOT NULL DEFAULT 10 COMMENT 'Job调度和运行状态',
  `accuracy_rate` decimal(5,2) NOT NULL DEFAULT 0 COMMENT '准确率例如99.99%',
  `precision_rate` decimal(5,2) NOT NULL DEFAULT 0 COMMENT '精度，例如99.99%',
  `recall_rate` decimal(5,2) NOT NULL DEFAULT 0 COMMENT '召回率，例如99.99%',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='jobpool'
