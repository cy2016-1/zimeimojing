<template>
  <div class="app-container">
    <el-tabs v-model="activeName">
      <el-tab-pane label="语音控制配置" name="yy_control">
        <dl class="ctable">
          <dt class="th xh">命令序号</dt>
          <dd class="th cfc">命令触发词</dd>
        </dl>
        <dl v-for="(item, index) in config_control" :key="index" class="ctable">
          <dt class="xh">
            <el-input :value="index" style="width:60px" />
          </dt>
          <dd class="cfc">
            <el-input v-for="(ite, ind) in item" :key="ind" v-model="item[ind]" class="cfcinput">
              <el-button slot="append" icon="el-icon-minus" @click="control_del(index,ind)" />
            </el-input>
            <el-input
              v-if="add_input==index"
              v-model="inputValue"
              style="width:auto"
              @keyup.enter.native="handleInputConfirm(index)"
              @blur="handleInputConfirm(index)"
            ></el-input>
            <el-button slot="append" type="primary" icon="el-icon-plus" plain title="添加" @click="control_add(index)" />
          </dd>
        </dl>
        <dl class="ctable">
          <dt class="xh">
            <el-input v-model="addIndex" style="width:60px" />
          </dt>
          <dd class="cfc">
            <el-input
              v-model="addValue"
              style="width:auto"
              @keyup.enter.native="addInputConfirm()"
              @blur="addInputConfirm()"
            />
          </dd>
        </dl>
        <div class="savebutt">
          <el-button type="success" @click="saveConfig">保存</el-button>
        </div>
      </el-tab-pane>
      <el-tab-pane label="语音命令配置" name="yy_command">
        <dl class="ctable">
          <dt class="th xh">命令序号</dt>
          <dd class="th cfc">命令对应功能</dd>
        </dl>
        <dl v-for="(item, index) in config_command" :key="index" class="ctable">
          <dt class="xh">
            <el-input :value="index" style="width:60px" />
          </dt>
          <dd class="cfc">
            <el-input v-model="config_command[index]" style="width:auto" />
            <el-button type="primary" plain title="删除" @click="command_del(index)">删除</el-button>
          </dd>
        </dl>
        <dl class="ctable">
          <dt class="xh">
            <el-input v-model="addCommIndex" style="width:60px" />
          </dt>
          <dd class="cfc">
            <el-input
              v-model="addCommText"
              style="width:auto"
              @keyup.enter.native="addInputCommand()"
              @blur="addInputCommand()"
            />
          </dd>
        </dl>
        <div class="savebutt">
          <el-button type="success" @click="saveCommand">保存</el-button>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
var request = import('/admin/utils/request.js').then((e) => { return e.default.request });

// 插件自定义配置
function customConfig(params) {
    return request.then((e) => {
        return e({
            url: '/plugin/CNW/configapi.py',
            method: 'post',
            params
        })
    })
}

module.exports = {
  data() {
    return {
      // tabs选项
      activeName: 'yy_control',
      // 插件配置目录
      pluginconfig_url: '',
      // 语音控制
      config_control: {},
      // 语音命令
      config_command: {},
      // 新增语音输入框
      add_input: false,
      inputValue: '',

      addIndex: '',
      addValue: '',

      addCommIndex: '',
      addCommText: ''
    }
  },

  // 页面载入后触发
  created() {
    this.fetchData()
  },

  methods: {
    // 加载基本数据
    fetchData() {
      customConfig({ op: 'getconfig' }).then(re => {
        var config_data = re.data
        this.config_control = config_data['control']
        this.config_command = config_data['command']
      })
    },

    // 删除控制
    control_del(index, ind) {
      this.config_control[index].splice(ind, 1)
      if (this.config_control[index].length <= 0) {
        delete this.config_control[index]
      }
      this.config_control = Object.assign({}, this.config_control)
    },

    // 添加控制
    control_add(index) {
      this.add_input = index
    },
    // 修改命令事件
    handleInputConfirm(index) {
      const inputValue = this.inputValue
      if (inputValue) {
        this.config_control[index].push(inputValue)
      }
      this.add_input = false
      this.inputValue = ''
    },

    // 增加命令事件
    addInputConfirm() {
      var addIndex = this.addIndex
      var inputValue = this.addValue
      if (addIndex === '' || inputValue === '') {
        return
      }
      if (this.config_control[addIndex]) {
        this.$message.error('新增的【' + addIndex + '】命令序号已存在。')
        this.addIndex = ''
        return
      } else {
        this.config_control[this.addIndex] = []
      }

      if (inputValue) {
        this.config_control[this.addIndex].push(inputValue)
      }
      this.addIndex = ''
      this.addValue = ''
    },

    // 保存语音控制
    saveConfig() {
      for (const key in this.config_control) {
        if (this.config_control.hasOwnProperty(key)) {
          const element = this.config_control[key]
          if (element.length <= 0) {
            this.$message.error('命令序号【' + key.toString() + '】触发词不能为空')
            return
          }
        }
      }
      var post_data = {
        op: 'setconfig',
        settype: 'control',
        data: this.config_control
      }
      customConfig(post_data).then(re => {
        var ret_data = re.data
        if (ret_data.error === 0) {
          this.$message({
            message: re.message,
            type: 'success'
          })
        }
      })
    },

    // ================================================

    addInputCommand() {
      var addIndex = this.addCommIndex
      var inputValue = this.addCommText
      if (addIndex === '' || inputValue === '') {
        return
      }
      if (this.config_command[addIndex] && this.config_command[addIndex] === inputValue) {
        this.$message.error('控制命令指令重复')
        return
      }
      this.config_command[addIndex] = inputValue
      this.config_command = Object.assign({}, this.config_command)
      this.addCommIndex = ''
      this.addCommText = ''
    },

    // 删除命令
    command_del(index) {
      delete this.config_command[index]
      this.config_command = Object.assign({}, this.config_command)
    },

    // 保存语音命令
    saveCommand() {
      var post_data = {
        op: 'setconfig',
        settype: 'command',
        data: this.config_command
      }
      customConfig(post_data).then(re => {
        var ret_data = re.data
        if (ret_data.error === 0) {
          this.$message({
            message: re.message,
            type: 'success'
          })
        }
      })
    }
  }
}
</script>

<style>
dl.ctable{margin:5px 0px;}
.ctable{list-style: none;list-style-type: none;width: 100%;float: left;}
.ctable dt,dl.ctable dd{float: left;margin: 0px;padding: 0px;}
.ctable .th{line-height: 30px;}
.ctable .xh{width: 100px;}
.ctable dd.cfc{position: absolute; width: 100%;left:100px;}
.ctable .cfcinput{margin-left:5px;width: auto;}
.savebutt{clear: both; padding: 15px 0 0 0;}
</style>
