/*
Navicat SQLite Data Transfer

Source Server         : 魔镜-本地
Source Server Version : 30706
Source Host           : :0

Target Server Type    : SQLite
Target Server Version : 30706
File Encoding         : 65001

Date: 2019-01-29 16:28:28
*/

PRAGMA foreign_keys = OFF;

-- ----------------------------
-- Table structure for "main"."device"
-- ----------------------------
DROP TABLE "main"."device";
CREATE TABLE "device" (
"clientid"  TEXT,
"mqtt_name"  TEXT,
"mqtt_pass"  TEXT,
PRIMARY KEY ("clientid")
);

-- ----------------------------
-- Records of device
-- ----------------------------
