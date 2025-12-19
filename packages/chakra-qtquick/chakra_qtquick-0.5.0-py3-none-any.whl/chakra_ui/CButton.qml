pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls

/*
    CButton - 按钮组件

    == 组件库特有属性 ==
    variant     : 按钮变体，可选 "solid" | "outline" | "ghost" | "link"，默认 "solid"
    colorScheme : 颜色方案，可选 "blue" | "green" | "red" | "orange" | "purple" | "primary" | "success" | "warning" | "error" 等，默认 "blue"
    size        : 尺寸，可选 "sm" | "md" | "lg"，默认 "md"
    fullWidth   : 是否全宽，默认 false
    leftIcon    : 左侧图标名称，默认 ""
    rightIcon   : 右侧图标名称，默认 ""
    iconOnly    : 仅图标按钮（无文字，正方形），默认 false
    isLoading   : 加载状态，默认 false
*/
Button {
    id: root

    // 变体: solid, outline, ghost, link
    property string variant: "solid"

    // 颜色方案: gray, red, green, blue, teal, pink, purple, cyan, orange, yellow, primary, secondary, success, warning, error
    property string colorScheme: "blue"

    // 尺寸: sm, md, lg
    property string size: "md"

    // 是否全宽
    property bool fullWidth: false

    // 左右图标
    property string leftIcon: ""
    property string rightIcon: ""

    // 仅图标按钮 (无文字，正方形)
    property bool iconOnly: false

    // 加载状态
    property bool isLoading: false

    enabled: !isLoading

    // 根据 colorScheme 获取颜色 (使用 AppStyle 辅助函数)
    property color schemeColor: AppStyle.getSchemeColor(colorScheme)
    property color schemeHover: AppStyle.getSchemeHover(colorScheme)
    property color schemeLight: AppStyle.getSchemeLight(colorScheme)

    // 尺寸配置 (使用 AppStyle 辅助函数)
    property int buttonHeight: AppStyle.getButtonHeight(size)
    property int fontSize: AppStyle.getFontSize(size === "lg" ? "md" : "sm")

    property int hPad: AppStyle.getCardPadding(size)

    implicitWidth: fullWidth ? parent.width : (iconOnly ? buttonHeight : contentItem.implicitWidth + hPad * 2)
    implicitHeight: buttonHeight

    // 文字颜色
    property color textColor: {
        if (!root.enabled)
            return AppStyle.textSecondary;
        if (root.variant === "solid")
            return AppStyle.textLight;
        if (root.variant === "outline")
            return AppStyle.textColor;
        if (root.variant === "link" || root.variant === "ghost")
            return root.schemeColor;
        return AppStyle.textColor;
    }

    contentItem: Item {
        implicitWidth: contentRow.implicitWidth
        implicitHeight: contentRow.implicitHeight

        Row {
            id: contentRow
            spacing: AppStyle.spacing2
            anchors.centerIn: parent

            // 加载指示器
            CSpinner {
                visible: root.isLoading
                size: "sm"
                color: root.variant === "solid" ? AppStyle.textLight : root.schemeColor
                anchors.verticalCenter: parent.verticalCenter
            }

            // 左侧图标
            CIcon {
                visible: root.leftIcon !== "" && !root.isLoading
                name: root.leftIcon
                size: root.fontSize
                iconColor: root.textColor
                anchors.verticalCenter: parent.verticalCenter
            }

            Text {
                visible: root.text !== ""
                text: root.text
                font.pixelSize: root.fontSize
                font.weight: Font.Medium
                color: root.textColor
                opacity: root.isLoading ? 0.7 : 1
                anchors.verticalCenter: parent.verticalCenter
            }

            // 右侧图标
            CIcon {
                visible: root.rightIcon !== ""
                name: root.rightIcon
                size: root.fontSize
                iconColor: root.textColor
                anchors.verticalCenter: parent.verticalCenter
            }
        }
    }

    background: Rectangle {
        id: bgOuter
        radius: AppStyle.radiusSm
        antialiasing: true

        color: {
            if (!root.enabled) {
                if (root.variant === "solid") {
                    return AppStyle.isDark ? Qt.rgba(255, 255, 255, 0.12) : Qt.rgba(0, 0, 0, 0.12);
                }
                return "transparent";
            }
            if (root.variant === "solid") {
                return root.hovered ? root.schemeHover : root.schemeColor;
            }
            if (root.variant === "outline") {
                return root.hovered ? (AppStyle.isDark ? Qt.rgba(255, 255, 255, 0.08) : Qt.rgba(0, 0, 0, 0.04)) : "transparent";
            }
            if (root.variant === "ghost" || root.variant === "link") {
                return root.hovered ? Qt.rgba(root.schemeColor.r, root.schemeColor.g, root.schemeColor.b, 0.1) : "transparent";
            }
            return "transparent";
        }

        border.width: root.variant === "outline" ? 1 : 0
        border.color: root.enabled ? AppStyle.borderColor : (AppStyle.isDark ? Qt.rgba(255, 255, 255, 0.1) : Qt.rgba(0, 0, 0, 0.1))

        Behavior on color {
            ColorAnimation {
                duration: AppStyle.durationFast
            }
        }
    }

    // 点击缩放效果
    scale: pressed ? 0.96 : 1
    transformOrigin: Item.Center

    Behavior on scale {
        NumberAnimation {
            duration: root.pressed ? 50 : 120
            easing.type: root.pressed ? Easing.OutCubic : Easing.OutBack
            easing.overshoot: 1.2
        }
    }
}
