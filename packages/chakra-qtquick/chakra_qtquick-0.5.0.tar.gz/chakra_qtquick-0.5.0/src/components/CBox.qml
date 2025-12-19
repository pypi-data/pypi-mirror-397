pragma ComponentBehavior: Bound

import QtQuick

/*
    CBox - 盒子布局组件

    == 组件库特有属性 ==
    p            : 内边距（四边），默认 0
    px           : 水平内边距，默认等于 p
    py           : 垂直内边距，默认等于 p
    pt/pb/pl/pr  : 上/下/左/右内边距
    m            : 外边距，默认 0
    w            : 宽度别名
    h            : 高度别名
    bg           : 背景色别名
    borderWidth  : 边框宽度
    borderColor  : 边框颜色
    cornerRadius : 圆角半径
    shadow       : 是否显示阴影，默认 false
    shadowSize   : 阴影大小，可选 "sm" | "md" | "lg" | "xl"，默认 "md"
*/
Rectangle {
    id: root

    // 内边距
    property int p: 0
    property int px: p
    property int py: p
    property int pt: py
    property int pb: py
    property int pl: px
    property int pr: px

    // 外边距 (通过 anchors.margins 实现)
    property int m: 0

    // 尺寸
    property alias w: root.width
    property alias h: root.height

    // 样式
    property alias bg: root.color
    property alias borderWidth: root.border.width
    property alias borderColor: root.border.color
    property alias cornerRadius: root.radius

    // 阴影
    property bool shadow: false
    property string shadowSize: "md"

    // 默认透明
    color: "transparent"

    // 内容区域
    default property alias content: contentContainer.data

    Item {
        id: contentContainer
        anchors.fill: parent
        anchors.topMargin: root.pt
        anchors.bottomMargin: root.pb
        anchors.leftMargin: root.pl
        anchors.rightMargin: root.pr

        // 自动设置子元素宽度
        Component.onCompleted: updateChildrenWidth()
        onChildrenChanged: updateChildrenWidth()
        onWidthChanged: updateChildrenWidth()

        function updateChildrenWidth() {
            for (let i = 0; i < children.length; i++) {
                let child = children[i];
                if (child && child.implicitWidth !== undefined) {
                    child.width = Qt.binding(() => contentContainer.width);
                }
            }
        }
    }

    // 阴影效果
    layer.enabled: shadow
    layer.effect: Item {
        property var shadowBlur: {
            switch (root.shadowSize) {
            case "sm":
                return 4;
            case "lg":
                return 15;
            case "xl":
                return 25;
            default:
                return 8;
            }
        }
    }
}
