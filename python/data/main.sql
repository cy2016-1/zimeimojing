/*
Navicat SQLite Data Transfer

Source Server         : 扫描-nmap
Source Server Version : 30706
Source Host           : :0

Target Server Type    : SQLite
Target Server Version : 30706
File Encoding         : 65001

Date: 2019-01-13 22:40:07
*/

PRAGMA foreign_keys = OFF;

-- ----------------------------
-- Table structure for "main"."nmap_config"
-- ----------------------------
DROP TABLE "main"."nmap_config";
CREATE TABLE "nmap_config" (
"key"  TEXT(20),
"value"  TEXT(20),
"nona"  TEXT(200)
);

-- ----------------------------
-- Records of nmap_config
-- ----------------------------
INSERT INTO "main"."nmap_config" VALUES ('endip', -120, '结束IP');
INSERT INTO "main"."nmap_config" VALUES ('is_nmapall', 0, '是否全局扫描');
INSERT INTO "main"."nmap_config" VALUES ('startip', '192.168.0.100', '开始IP');

-- ----------------------------
-- Table structure for "main"."nmap_mon"
-- ----------------------------
DROP TABLE "main"."nmap_mon";
CREATE TABLE "nmap_mon" (
"mac"  TEXT(20),
"ip"  TEXT(15),
"notename"  TEXT(30),
"up_time"  TEXT(11),
"is_online"  INTEGER,
PRIMARY KEY ("mac")
);

-- ----------------------------
-- Records of nmap_mon
-- ----------------------------

-- ----------------------------
-- Table structure for "main"."nmap_mon_list"
-- ----------------------------
DROP TABLE "main"."nmap_mon_list";
CREATE TABLE "nmap_mon_list" (
"id"  INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
"mac"  TEXT(20),
"up_time"  TEXT(20),
"jiange"  INTEGER
);

-- ----------------------------
-- Records of nmap_mon_list
-- ----------------------------

-- ----------------------------
-- Table structure for "main"."nmap_online"
-- ----------------------------
DROP TABLE "main"."nmap_online";
CREATE TABLE "nmap_online" (
"mac"  TEXT(20),
"ip"  TEXT(15),
"name"  TEXT(50),
"notename"  TEXT(50),
"up_time"  TEXT(11),
"is_online"  INTEGER,
PRIMARY KEY ("mac")
);

-- ----------------------------
-- Records of nmap_online
-- ----------------------------

-- ----------------------------
-- Table structure for "main"."sqlite_sequence"
-- ----------------------------
DROP TABLE "main"."sqlite_sequence";
CREATE TABLE sqlite_sequence(name,seq);

-- ----------------------------
-- Records of sqlite_sequence
-- ----------------------------
INSERT INTO "main"."sqlite_sequence" VALUES ('nmap_mon_list', null);
