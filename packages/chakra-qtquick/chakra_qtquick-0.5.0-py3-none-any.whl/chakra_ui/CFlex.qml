import QtQuick
import QtQuick.Layouts

/*
    CFlex - 弹性布局组件

    == 组件库特有属性 ==
    direction : 排列方向，可选 "row" | "column"，默认 "row"
    wrap      : 是否换行，默认 false
    justify   : 主轴对齐，可选 "start" | "center" | "end" | "between" | "around"，默认 "start"
    align     : 交叉轴对齐，可选 "start" | "center" | "end" | "stretch"，默认 "stretch"
    gap       : 子元素间距，默认 0
    p         : 内边距（四边），默认 0
    px        : 水平内边距
    py        : 垂直内边距
*/
Item {
    id: root

    // Flex 方向
    property string direction: "row"  // row, column
    property bool wrap: false

    // 对齐
    property string justify: "start"  // start, center, end, between, around
    property string align: "stretch"   // start, center, end, stretch

    // 间距
    property int gap: 0

    // 内边距
    property int p: 0
    property int px: p
    property int py: p

    // 内容
    default property alias content: layout.data

    implicitWidth: layout.implicitWidth + px * 2
    implicitHeight: layout.implicitHeight + py * 2

    GridLayout {
        id: layout
        anchors.fill: parent
        anchors.margins: root.p
        anchors.leftMargin: root.px
        anchors.rightMargin: root.px
        anchors.topMargin: root.py
        anchors.bottomMargin: root.py

        columns: root.direction === "row" ? (root.wrap ? -1 : children.length) : 1
        rows: root.direction === "column" ? (root.wrap ? -1 : children.length) : 1

        columnSpacing: root.direction === "row" ? root.gap : 0
        rowSpacing: root.direction === "column" ? root.gap : 0

        // 对齐方式映射
        property int hAlign: {
            if (root.direction === "row") {
                switch (root.justify) {
                case "center":
                    return Qt.AlignHCenter;
                case "end":
                    return Qt.AlignRight;
                default:
                    return Qt.AlignLeft;
                }
            } else {
                switch (root.align) {
                case "center":
                    return Qt.AlignHCenter;
                case "end":
                    return Qt.AlignRight;
                default:
                    return Qt.AlignLeft;
                }
            }
        }

        property int vAlign: {
            if (root.direction === "column") {
                switch (root.justify) {
                case "center":
                    return Qt.AlignVCenter;
                case "end":
                    return Qt.AlignBottom;
                default:
                    return Qt.AlignTop;
                }
            } else {
                switch (root.align) {
                case "center":
                    return Qt.AlignVCenter;
                case "end":
                    return Qt.AlignBottom;
                default:
                    return Qt.AlignTop;
                }
            }
        }
    }
}
