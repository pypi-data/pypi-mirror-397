pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Effects

/**
 * CProgress - 进度条组件
 * 
 * 显示任务进度，支持条纹样式、动画和不确定状态。
 * 
 * @component
 * @example
 * CProgress {
 *     value: 75
 *     colorScheme: "primary"
 *     hasStripe: true
 *     isAnimated: true
 * }
 * 
 * @property {real} value - 进度值（0-100）
 *   默认值: 0
 * 
 * @property {string} colorScheme - 颜色方案
 *   默认值: "primary"
 * 
 * @property {string} size - 尺寸
 *   可选值: "xs" | "sm" | "md" | "lg"
 *   默认值: "md"
 * 
 * @property {bool} hasStripe - 是否显示条纹效果
 *   默认值: false
 * 
 * @property {bool} isAnimated - 是否动画条纹（需配合 hasStripe）
 *   默认值: false
 *   注意: 使用 Timer 限制帧率，优化性能
 * 
 * @property {bool} isIndeterminate - 是否不确定状态（加载中）
 *   默认值: false
 */
Item {
    id: root

    // 值 (0-100)
    property real value: 0

    // 颜色方案
    property string colorScheme: "primary"

    // 尺寸: xs, sm, md, lg
    property string size: "md"

    // 是否显示条纹
    property bool hasStripe: false

    // 是否动画条纹
    property bool isAnimated: false

    // 是否不确定状态
    property bool isIndeterminate: false

    property color schemeColor: AppStyle.getSchemeColor(colorScheme)

    property int trackHeight: AppStyle.getProgressHeight(size)

    implicitWidth: 200
    implicitHeight: trackHeight

    // 背景轨道
    Rectangle {
        id: track
        anchors.fill: parent
        radius: height / 2
        color: AppStyle.borderColor
    }

    // 填充层 - 使用 layer mask 裁剪为圆角
    Item {
        id: fillContainer
        anchors.fill: parent

        layer.enabled: true
        layer.effect: MultiEffect {
            maskEnabled: true
            maskThresholdMin: 0.5
            maskSpreadAtMin: 1.0
            maskSource: ShaderEffectSource {
                sourceItem: Rectangle {
                    width: fillContainer.width
                    height: fillContainer.height
                    radius: track.radius
                }
            }
        }

        // 填充条
        Rectangle {
            id: fill
            height: parent.height
            radius: track.radius
            color: root.schemeColor

            width: root.isIndeterminate ? parent.width * 0.3 : parent.width * (root.value / 100)

            x: root.isIndeterminate ? indeterminateAnim.x : 0

            Behavior on width {
                enabled: !root.isIndeterminate
                NumberAnimation {
                    duration: AppStyle.durationNormal
                }
            }

            // 条纹效果 - Canvas 实现（兼容性好，无需 GPU）
            Canvas {
                id: stripeCanvas
                visible: root.hasStripe
                anchors.fill: parent

                property real offset: 0

                onPaint: {
                    var ctx = getContext("2d");
                    ctx.reset();

                    var stripeWidth = 20;
                    ctx.fillStyle = Qt.rgba(1, 1, 1, 0.15);

                    for (var i = -stripeWidth; i < width + stripeWidth * 2; i += stripeWidth * 2) {
                        ctx.beginPath();
                        ctx.moveTo(i + offset, 0);
                        ctx.lineTo(i + stripeWidth + offset, 0);
                        ctx.lineTo(i + offset, height);
                        ctx.lineTo(i - stripeWidth + offset, height);
                        ctx.closePath();
                        ctx.fill();
                    }
                }

                Timer {
                    id: animTimer
                    interval: 33
                    running: root.visible && root.isAnimated && root.hasStripe
                    repeat: true
                    onTriggered: {
                        stripeCanvas.offset = (stripeCanvas.offset + 2) % 40
                        stripeCanvas.requestPaint()
                    }
                }
            }
        }
    }

    // 不确定状态动画
    SequentialAnimation {
        id: indeterminateAnim
        running: root.visible && root.isIndeterminate
        loops: Animation.Infinite

        property real x: 0

        NumberAnimation {
            target: indeterminateAnim
            property: "x"
            from: -track.width * 0.3
            to: track.width
            duration: 1500
            easing.type: Easing.InOutQuad
        }
    }
}
