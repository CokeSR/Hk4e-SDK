import pymysql
from src.tools.loadconfig            import loadConfig
from src.tools.logger.system         import logger              as sys_log

# ===================== 数据库重建 ===================== #
def initializeDatabase():
    sys_log.info(f"正在初始化数据库结构(清空数据)...")
    func = [init_db, init_db_cdk, init_db_ann]
    for f in func:
        if f():
            continue
        else:
            sys_log.error(f"初始化数据库失败")

# 账号管理库
def init_db():
    config = loadConfig()["Database"]["mysql"]
    conn = pymysql.connect(
        host=config["host"],
        user=config["user"],
        port=config["port"],
        password=config["password"],
        charset="utf8",
        autocommit=True
    )
    cursor = conn.cursor()
    try:
        cursor.execute(
            "CREATE DATABASE IF NOT EXISTS `{}` CHARACTER SET utf8 COLLATE utf8_general_ci".format(
                config["account_library_name"]
            )
        )
        cursor.execute("USE `{}`".format(config["account_library_name"]))
        cursor.execute("DROP TABLE IF EXISTS `t_accounts`")
        cursor.execute("DROP TABLE IF EXISTS `t_accounts_tokens`")
        cursor.execute("DROP TABLE IF EXISTS `t_accounts_guests`")
        cursor.execute("DROP TABLE IF EXISTS `t_accounts_events`")
        cursor.execute("DROP TABLE IF EXISTS `t_accounts_thirdparty`")
        cursor.execute("DROP TABLE IF EXISTS `t_accounts_realname`")
        cursor.execute("DROP TABLE IF EXISTS `t_thirdparty_tokens`")
        cursor.execute("DROP TABLE IF EXISTS `t_combo_tokens`")
        cursor.execute("DROP TABLE IF EXISTS `t_ip_blacklist`")
        cursor.execute("DROP TABLE IF EXISTS `t_verifykey_config`")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS `t_accounts` (
                `uid` INT AUTO_INCREMENT PRIMARY KEY COMMENT '玩家UID',
                `name` VARCHAR(255) COMMENT '用户名',
                `mobile` VARCHAR(255) UNIQUE COMMENT '手机号',
                `email` VARCHAR(255) UNIQUE COMMENT '电子邮件',
                `password` VARCHAR(255) COMMENT '哈希密码',
                `type` INT NOT NULL COMMENT '1 注册 0 未注册',
                `epoch_created` INT NOT NULL COMMENT '时间戳'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci
            COMMENT='玩家账号信息表'
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS `t_accounts_tokens` (
                `uid` INT NOT NULL COMMENT '玩家UID',
                `token` VARCHAR(255) NOT NULL COMMENT '登录Token',
                `device` VARCHAR(255) DEFAULT NULL COMMENT '设备ID',
                `ip` VARCHAR(255) NOT NULL COMMENT '登录IP',
                `epoch_generated` INT NOT NULL COMMENT '时间戳',
                PRIMARY KEY(`uid`,`token`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci
            COMMENT='账号登录token'
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS `t_accounts_guests` (
                `uid` INT NOT NULL COMMENT '玩家UID',
                `device` VARCHAR(255) NOT NULL COMMENT '设备ID',
                PRIMARY KEY(`uid`,`device`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci
            COMMENT='游客登录信息表'
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS `t_accounts_events` (
                `uid` INT NOT NULL COMMENT '玩家UID',
                `method` VARCHAR(255) NOT NULL COMMENT '登录方式',
                `account_type` INT NOT NULL COMMENT '账号类型',
                `account_id` INT NOT NULL COMMENT '账号ID',
                `platform` INT NOT NULL COMMENT '平台',
                `region` VARCHAR(255) NOT NULL COMMENT '区服信息',
                `biz_game` VARCHAR(255) NOT NULL,
                `epoch_created` INT NOT NULL COMMENT '时间戳',
                PRIMARY KEY(`epoch_created`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci
            COMMENT='账号活动记录表 由GameServer控制'
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS `t_accounts_thirdparty` (
                `uid` INT NOT NULL COMMENT '玩家UID',
                `type` INT NOT NULL COMMENT '类型',
                `external_name` VARCHAR(255) NOT NULL COMMENT '标识名称',
                `external_id` INT NOT NULL COMMENT '标识ID',
                PRIMARY KEY(`uid`,`type`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci
            COMMENT='第三方账号登录信息表'
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS `t_thirdparty_tokens` (
                `uid` INT NOT NULL COMMENT '玩家UID',
                `type` INT NOT NULL COMMENT '类型',
                `token` VARCHAR(255) NOT NULL COMMENT '登录Token'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci
            COMMENT='第三方账号登录token'
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS `t_combo_tokens` (
                `uid` INT NOT NULL COMMENT '玩家UID',
                `token` VARCHAR(255) NOT NULL COMMENT '登录Token',
                `device` VARCHAR(255) NOT NULL COMMENT '设备ID',
                `ip` VARCHAR(255) NOT NULL COMMENT '登录IP',
                `epoch_generated` INT NOT NULL COMMENT '时间戳',
                PRIMARY KEY(`uid`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci
            COMMENT='设备信息token'
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS `t_accounts_realname`  (
                `account_id` INT NOT NULL COMMENT '账号ID',
                `ticket` varchar(255) NOT NULL COMMENT '实名认证 Ticket',
                `action_type` varchar(255) NOT NULL COMMENT '操作请求',
                `epoch_created` INT NOT NULL COMMENT '时间',
                `name` varchar(255) COMMENT '名字',
                `identity_card` varchar(255) COMMENT '身份证号',
                PRIMARY KEY (`account_id`) USING BTREE
            ) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci
            COMMENT='实名认证记录'
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS `t_ip_blacklist`  (
                `id` int NOT NULL AUTO_INCREMENT COMMENT '序号',
                `ip_address` varchar(45) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '访问IP',
                `city` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '归属地',
                `blacklisted_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '被封禁的时间戳',
                PRIMARY KEY (`id`) USING BTREE
            ) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8 COLLATE = utf8_general_ci
            COMMENT = 'IP 黑名单记录表'
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS `t_verifykey_config`  (
                `id` int UNSIGNED NOT NULL COMMENT '序号',
                `type` varchar(16) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '' COMMENT '只允许authkey或rsakey',
                `version` int UNSIGNED NOT NULL COMMENT '客户端参数对接',
                `public_key` varchar(4096) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '' COMMENT '加密公钥',
                `private_key` varchar(4096) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '' COMMENT '解密私钥',
                PRIMARY KEY (`id`) USING BTREE
            ) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci
            COMMENT = '密钥管理';
            """
        )
        # 默认秘钥
        cursor.execute(
            """
            INSERT INTO `t_verifykey_config` VALUES (1, 'authkey', 1, '-----BEGIN RSA PUBLIC KEY-----\nMIIBCgKCAQEAw5pG0SFrw880NHSNbtH3WYLgJGQwx9Gra1UQmVgpMcp8USrpqWN0\nhneoxbMQT1pHwnAWDlliVMdlGSWqTgFfWdes4VXHFbkZ+5VPJFt+0dp6nuO+taGB\n1y7EbITOPTkMqTVCFxZbIjHjhSAw/h5xmlOAIC1tcZIDU+NOJW9ZCYMT6vK29rMr\nO2dsHg9+cAyqnz/GycBQFhlk/1PCSH10OGdsohFGiIWNLqqlwkVHmizGiLyy1FeY\n3s700pmtVXB5WQjQ/jojp3jFZTmGmL9hGxZpWOsjrmWASp7pjFFUd6UNxQH7BMWv\n9tVH50hin7R2mrUftWKSD99dathlgGvO8wIDAQAB\n-----END RSA PUBLIC KEY-----', '-----BEGIN RSA PRIVATE KEY-----\nMIIEpgIBAAKCAQEAw5pG0SFrw880NHSNbtH3WYLgJGQwx9Gra1UQmVgpMcp8USrp\nqWN0hneoxbMQT1pHwnAWDlliVMdlGSWqTgFfWdes4VXHFbkZ+5VPJFt+0dp6nuO+\ntaGB1y7EbITOPTkMqTVCFxZbIjHjhSAw/h5xmlOAIC1tcZIDU+NOJW9ZCYMT6vK2\n9rMrO2dsHg9+cAyqnz/GycBQFhlk/1PCSH10OGdsohFGiIWNLqqlwkVHmizGiLyy\n1FeY3s700pmtVXB5WQjQ/jojp3jFZTmGmL9hGxZpWOsjrmWASp7pjFFUd6UNxQH7\nBMWv9tVH50hin7R2mrUftWKSD99dathlgGvO8wIDAQABAoIBAQCA2gx0j3OSFdjq\nBS12J1Kt4I0O7AFGYFRv7CV3HqBkcGLchUxPjXihbAn90iuYWnyTFYsyAKfJ+WAb\n5Lf/kt/hKzZzajIvmTQIix8LcEpmq2nDaXuj4rTJr8EtS38gzYgNn0veMZfvOrYK\naF5dyGhFpWPtzn8eJXWTuVUtS+B3Zn2b8Cm1uSo0cNnnqrGXtJxuSG5lZfjiAj1J\nZflsBMMfGk6AVA+wrKOn0tEN/V5Bqpy6g7dlp3HA1jL4CHTn79p4MHuISS8bmTVG\nkIZAdBp7FdAXRjGTwyx0psZw+P9xDjYZBUwDo7hKsxhMIrWkPoJnTVe/IN263ZfO\nGMQHCL0BAoGBAPT/1TTAPa6FrAcwU1O8qcFDjhSSLZ7trIMjf4O4kGWCPvMC4alD\nGNI07fh/03YJuhUt9bsonBXvxLMthU9+5uSBBYnybCno+Tm37J4z9/oU44brsbQi\niZTDuZcQL4UXgrqn/N4Fnl22P8zCdmrj7KTEv5Cxt8Z+quWmIoGrUaGhAoGBAMxi\nph7p2l1kJNvsl8xI2daUSGEiadWRGlIBMOXphhMHe3t64W+nsN+SQn6fgP9S9ohu\nuOoYa47WzKi9CgsOXh0iJCFN8+3/oQIPamLBLKpeE4JPfaWRGLXyUvUIgUDPyy+Q\nIdrKi9fY9Xpjrn9FQWNRXv7e5iKeKNp3HzzNytATAoGBANuACijEw36EzGd0aHNx\naDV6rOTJQo5NKm4jc68zwErxsixOvJbFQouyWDJ3c6EhfdJT5wDTlWQh+Pz/H5zl\neT/oSGobA8VYsVGA80GaFeW8qUzMBd35w4HBCZnKKoj3U2yf7PGN3yDek7KD10xV\nAENu8qJUVu5DtiEiA3BhaTWBAoGBAIdOy8FtehYX5Vr/f+NLW4P2eRBtUvmDbZRa\nm3+qIQvaCULPMA3WS39HeeQQPrtJtlLOUncQIazXwXf4Zny5T08kOh0eWV33vST7\nBahJUQOc8ndznrAMpfpWads0fTVmG5Lqba9GJlyIksMq2OwC8m4JAcXj1SGX6V3w\nPOrpJtqnAoGBAKMUp7OgARXc9U+57+fuF5q5gyrIDkZnTWU4r6GG4aAmReuyMwim\nqvx+sdasd3D6xp0GqaEAM6BHr+DXE19OW+gIg4MJht1izO7xqpNfzlwL1xCHhJtV\nYDQ7N1vkdn7/T0sycRe7MAexaKj7MDrOjxhxzMnj6+f0WTZYSCqD3GUK\n-----END RSA PRIVATE KEY-----');    
            """
        )
        cursor.execute(
            """
            INSERT INTO `t_verifykey_config` VALUES (2, 'rsakey', 1, '-----BEGIN RSA PUBLIC KEY-----\nMIIBCgKCAQEAxbbx2m1feHyrQ7jP+8mtDF/pyYLrJWKWAdEv3wZrOtjOZzeLGPzs\nmkcgncgoRhX4dT+1itSMR9j9m0/OwsH2UoF6U32LxCOQWQD1AMgIZjAkJeJvFTrt\nn8fMQ1701CkbaLTVIjRMlTw8kNXvNA/A9UatoiDmi4TFG6mrxTKZpIcTInvPEpkK\n2A7Qsp1E4skFK8jmysy7uRhMaYHtPTsBvxP0zn3lhKB3W+HTqpneewXWHjCDfL7N\nbby91jbz5EKPZXWLuhXIvR1Cu4tiruorwXJxmXaP1HQZonytECNU/UOzP6GNLdq0\neFDE4b04Wjp396551G99YiFP2nqHVJ5OMQIDAQAB\n-----END RSA PUBLIC KEY-----', '-----BEGIN RSA PRIVATE KEY-----\nMIIEpQIBAAKCAQEAxbbx2m1feHyrQ7jP+8mtDF/pyYLrJWKWAdEv3wZrOtjOZzeL\nGPzsmkcgncgoRhX4dT+1itSMR9j9m0/OwsH2UoF6U32LxCOQWQD1AMgIZjAkJeJv\nFTrtn8fMQ1701CkbaLTVIjRMlTw8kNXvNA/A9UatoiDmi4TFG6mrxTKZpIcTInvP\nEpkK2A7Qsp1E4skFK8jmysy7uRhMaYHtPTsBvxP0zn3lhKB3W+HTqpneewXWHjCD\nfL7Nbby91jbz5EKPZXWLuhXIvR1Cu4tiruorwXJxmXaP1HQZonytECNU/UOzP6GN\nLdq0eFDE4b04Wjp396551G99YiFP2nqHVJ5OMQIDAQABAoIBAQDEeYZhjyq+avUu\neSuFhOaIU4/ZhlXycsOqzpwJvzEz61tBSvrZPA5LSb9pzAvpic+7hDH94jX89+8d\nNfO7qlADsVNEQJBxuv2o1MCjpCRkmBZz506IBGU60Kt1j5kwdCEergTW1q375z4w\nl8f7LmSL2U6WvKcdojTVxohBkIUJ7shtmmukDi2YnMfe6T/2JuXDDL8rvIcnfr5E\nMCgPQs+xLeLEGrIJdpUy1iIYZYrzvrpJwf9EJL3D0e7jkpbvAQZ8EF9YhEizJhOm\ndzTqW4PgW2yUaHYd3q5QjiILy7AC+oOYoTZln3RfjPOxl+bYjeMOWlqkgtpPQkAE\n4I64w8RZAoGBAPLR44pEkmTdfIIF8ZtzBiVfDZ29bT96J0CWXGVzp8x6bSu5J5jl\ns7sP8DEcjGZ6vHsLGOvkcNxzcnR3l/5HOz6TIuvVuUm36b1jHltq1xZStjGeKZs1\nihhJSu2lIA+TrK8FCRnKARJ0ughXGNZFItgeM230Sgjp2RL4ISXJ724XAoGBANBy\nS2RwNpUYvkCSZHSFnQM/jq1jldxw+0p4jAGpWLilEaA/8xWUnZrnCrPFF/t9llpb\ndTR/dCI8ntIMAy2dH4IUHyYKUahyHSzCAUNKpS0s433kn5hy9tGvn7jyuOJ4dk9F\no1PIZM7qfzmkdCBbX3NF2TGpzOvbYGJHHC3ssVr3AoGBANHJDopN9iDYzpJTaktA\nVEYDWnM2zmUyNylw/sDT7FwYRaup2xEZG2/5NC5qGM8NKTww+UYMZom/4FnJXXLd\nvcyxOFGCpAORtoreUMLwioWJzkkN+apT1kxnPioVKJ7smhvYAOXcBZMZcAR2o0m0\nD4eiiBJuJWyQBPCDmbfZQFffAoGBAKpcr4ewOrwS0/O8cgPV7CTqfjbyDFp1sLwF\n2A/Hk66dotFBUvBRXZpruJCCxn4R/59r3lgAzy7oMrnjfXl7UHQk8+xIRMMSOQwK\np7OSv3szk96hy1pyo41vJ3CmWDsoTzGs7bcdMl72wvKemRaU92ckMEZpzAT8cEMC\ncWKLb8yzAoGAMibG8IyHSo7CJz82+7UHm98jNOlg6s73CEjp0W/+FL45Ka7MF/lp\nxtR3eSmxltvwvjQoti3V4Qboqtc2IPCt+EtapTM7Wo41wlLCWCNx4u25pZPH/c8g\n1yQ+OvH+xOYG+SeO98Phw/8d3IRfR83aqisQHv5upo2Rozzo0Kh3OsE=\n-----END RSA PRIVATE KEY-----');
            """
        )
        conn.commit()
        conn.close()
        sys_log.info(f"导入 {config['account_library_name']} 成功")
        return True
    except Exception as err:
        sys_log.error(f"导入 {config['account_library_name']} 时出现意外错误：{err}")
        return False


# CDK管理库
def init_db_cdk():
    config = loadConfig()["Database"]["mysql"]
    conn = pymysql.connect(
        host=config["host"],
        user=config["user"],
        port=config["port"],
        password=config["password"],
        charset="utf8",
        autocommit=True
    )
    cursor = conn.cursor()
    try:
        cursor.execute(
            "CREATE DATABASE IF NOT EXISTS `{}` CHARACTER SET utf8 COLLATE utf8_general_ci".format(
                config["exchcdk_library_name"]
            )
        )
        cursor.execute("USE `{}`".format(config["exchcdk_library_name"]))
        cursor.execute("DROP TABLE IF EXISTS `t_cdk_record`")
        cursor.execute("DROP TABLE IF EXISTS `t_cdk_template`")
        cursor.execute("DROP TABLE IF EXISTS `t_cdk_redeem`")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS `t_cdk_record` (
                `cdk_name` varchar(255) NOT NULL COMMENT '使用的CDK',
                `uid` INT NOT NULL COMMENT '玩家UID',
                `account_type` varchar(255) NOT NULL COMMENT '账号类型',
                `account_uid` INT NOT NULL COMMENT '账号ID',
                `region` varchar(255) NOT NULL COMMENT '所在区服',
                `game` varchar(255) NOT NULL COMMENT 'cn/global',
                `platform` varchar(255) NOT NULL COMMENT '客户端平台',
                `used_time` varchar(255) NOT NULL COMMENT '使用时间'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci
            COMMENT '玩家CDK兑换记录'
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS `t_cdk_redeem` (
                `cdk_name` varchar(255) NOT NULL COMMENT 'CDK配置',
                `open_time` datetime NOT NULL COMMENT '启用时间',
                `expire_time` datetime NOT NULL COMMENT '过期时间',
                `enabled` INT NOT NULL COMMENT '1启用0不启用',
                `template_id` INT NOT NULL COMMENT '与CDK邮件配置相对应',
                `times` INT NOT NULL COMMENT '使用次数',
                PRIMARY KEY (`cdk_name`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci
            COMMENT 'CDK配置'
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS `t_cdk_template` (
                `cdk_template_id` int NOT NULL COMMENT '与CDK配置相对应',
                `title` varchar(255) NOT NULL COMMENT '邮件标头',
                `sender` varchar(255) NOT NULL COMMENT '署名',
                `content` varchar(255) NOT NULL COMMENT '邮件内容',
                `importance` INT NOT NULL COMMENT '是否是星标邮件(0/1)',
                `is_collectible` varchar(255) NOT NULL COMMENT '是否纳入收藏夹(true/false)',
                `item_list` varchar(255) NOT NULL COMMENT '物品id:数量 逗号分隔',
                PRIMARY KEY (`cdk_template_id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci
            COMMENT 'CDK邮件配置'
            """
        )
        conn.commit()
        conn.close()
        sys_log.info(f"导入 {config['exchcdk_library_name']} 成功")
        return True
    except Exception as err:
        sys_log.error(f"导入 {config['exchcdk_library_name']}时出现意外错误：{err}")
        return False


# 公告管理库
def init_db_ann():
    config = loadConfig()["Database"]["mysql"]
    conn = pymysql.connect(
        host=config["host"],
        user=config["user"],
        port=config["port"],
        password=config["password"],
        charset="utf8",
        autocommit=True
    )
    cursor = conn.cursor()
    try:
        cursor.execute(
            "CREATE DATABASE IF NOT EXISTS `{}` CHARACTER SET utf8 COLLATE utf8_general_ci".format(
                config["announce_library_name"]
            )
        )
        cursor.execute("USE `{}`".format(config["announce_library_name"]))
        cursor.execute("DROP TABLE IF EXISTS `t_announce_content`")
        cursor.execute("DROP TABLE IF EXISTS `t_announce_list`")
        cursor.execute("DROP TABLE IF EXISTS `t_announce_config`")

        cursor.execute(
            """
            CREATE TABLE `t_announce_config`  (
                `id` int NOT NULL COMMENT '序列ID，与 list 表对应',
                `mi18n_name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '列表头部',
                PRIMARY KEY (`id`) USING BTREE,
                INDEX `mi18n_name`(`mi18n_name` ASC) USING BTREE
            ) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = '公告展示设置（父）' ROW_FORMAT = Dynamic;
            """
        )
        cursor.execute(
            """
            CREATE TABLE `t_announce_list`  (
                `type_id` int NOT NULL COMMENT '公告列表内容ID，与config表对应',
                `ann_id` int NOT NULL COMMENT '公告ID',
                `start_time` datetime NOT NULL COMMENT '开启时间',
                `end_time` datetime NOT NULL COMMENT '结束时间',
                `tag_icon` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '左侧标签URL',
                `login_alert` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '红点显示',
                `desc` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '备注',
                PRIMARY KEY (`ann_id`) USING BTREE,
                INDEX `id`(`type_id` ASC) USING BTREE,
                CONSTRAINT `id` FOREIGN KEY (`type_id`) REFERENCES `t_announce_config` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
            ) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = '公告显示配置' ROW_FORMAT = Dynamic;
            """
        )
        cursor.execute(
            """
            CREATE TABLE `t_announce_content`  (
                `ann_id` int NOT NULL COMMENT '公告ID，与 list 绑定',
                `subtitle` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '公告左侧标头',
                `title` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '公告右侧标头',
                `banner` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '图片URL',
                `content` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL COMMENT '公告内容，压缩h5形式',
                `desc` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '备注',
                PRIMARY KEY (`ann_id`) USING BTREE,
                CONSTRAINT `ann_id` FOREIGN KEY (`ann_id`) REFERENCES `t_announce_list` (`ann_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
            ) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = '公告内容设置' ROW_FORMAT = Dynamic;
            """
        )

        data = [
            "INSERT INTO `t_announce_config` VALUES (1, '游戏公告');",
            "INSERT INTO `t_announce_config` VALUES (2, '活动公告');",
            "INSERT INTO `t_announce_config` VALUES (3, 'SDK 说明');",
            "INSERT INTO `t_announce_list` VALUES (3, 3646, '2024-08-10 00:00:00', '2025-08-31 00:00:00', 'https://sdk-webstatic.mihoyo.com/announcement/2020/03/05/f3016cc0dbe3f9c2305566742ae5927f_1830032474842461374.png', '1', '');",
            "INSERT INTO `t_announce_content` VALUES (3646, 'code.cokeserver', 'Thank you for using SDK by Cokesr', '', '<span>SDK version: 1.4.2</span><p style=\"white-space: pre-wrap;\"><strong>〓项目地址〓</strong><br><a href=\"https://code.cokeserver.com/Coke/Hk4e-SDK\">Hk4e-SDK</a><p style=\"white-space: pre-wrap; min-height: 1.5em;\"><strong>〓QQ交流群〓</strong><br><a href=\"http://qm.qq.com/cgi-bin/qm/qr?_wv=1027&k=VufQMsKKQ4qgP4TX4SHDzwZp2bPap3BJ&authKey=IpEWy908iDHJyAxs6%2F%2BHVx0MGlbtYLlhiBBEahU5tIc3j7wrPRgNSBgn9L1KPnZ%2F&noverify=0&group_code=498902680\">CokeSR@我不是O神</a></p>', 'SDK');",
        ]

        for sql in data:
            cursor.execute(sql)

        conn.commit()
        conn.close()
        sys_log.info(f"导入 {config['announce_library_name']} 成功")
        return True
    except Exception as err:
        sys_log.error(f"导入 {config['announce_library_name']}时出现意外错误：{err}")
        return False
