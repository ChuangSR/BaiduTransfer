var function_list = [
    {
    key: "getRandomInt",
    value: function getRandomInt(num) {
        return Math.floor((Math.random() * 9 + 1) * Math.pow(10, num - 1))
    }
}, {
    key: "prefixInteger",
    value: function prefixInteger(num, length) {
        num += "";
        return new Array(length - num.length).fill("0").join("") + num
    }
}, {
    key: "getCountId",
    value: function getCountId() {
        if (this._countId < 9999) {
            this._countId += 1
        } else {
            this._countId = 0
        }
        return this.prefixInteger(this._countId, 4)
    }
}, {
    key: "validateUk",
    value: function validateUk(uk) {
        return (uk + "").length === 10
    }
}, {
    key: "getDpLogId",
    value: function getDpLogId(uk) {
        var innerUserId = this.userId;
        if (uk && this.validateUk(uk)) {
            innerUserId = uk
        }
        return "".concat(this.client).concat(this.sessionId).concat(innerUserId).concat(this.getCountId())
    }
}, {
    key: "getDpLogIdByUrl",
    value: function getDpLogIdByUrl(str) {
        var matchArr = /dp-logid=(\d+)/.exec(str);
        if (matchArr && matchArr[1]) {
            return matchArr[1]
        }
        return this.getDpLogId()
    }
}, {
    key: "addDpLogId",
    value: function addDpLogId(url, uk, dpLogId) {
        var reg = /dp-logid=\d+/;
        if (reg.test(url)) {
            return url
        }
        var logId = dpLogId || this.getDpLogId(uk);
        url += /\?/.test(url) ? "&" : "?";
        url += "dp-logid=".concat(logId);
        return url
    }
}
]
function _defineProperties(target, props) {
    for (var i = 0; i < props.length; i++) {
        var descriptor = props[i];
        descriptor.enumerable = descriptor.enumerable || false;
        descriptor.configurable = true;
        if ("value" in descriptor)
            descriptor.writable = true;
        Object.defineProperty(target, descriptor.key, descriptor)
    }
}

var DpLogId = function () {
    function DpLogId() {
        this.sessionId = this.getRandomInt(6);
        this.userId = "00" + this.getRandomInt(8);
        this._countId = 10;
        this.client = ""
    }
    _defineProperties(DpLogId.prototype,function_list)
    return new DpLogId()
}();
//获取生成dp-logid参数
function get_dp_logid(){
    return DpLogId.getDpLogId()
}