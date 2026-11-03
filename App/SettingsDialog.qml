import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: root

    required property var settingsStore

    title: qsTr("Settings")

    parent: Overlay.Overlay
    anchors.centerIn: parent
    width: 720
    height: 480
    modal: true
    focus: true

    closePolicy: Popup.CloseOnEscape

    standardButtons: Dialog.Ok | Dialog.Cancel

    ColumnLayout {
        spacing: 10
        anchors.fill: parent
        width: root.availableWidth

        Label {
            text: qsTr("Ollama URL")
        }

        TextField {
            id: ollamaUrlField
            Layout.fillWidth: true
            placeholderText: "http://localhost:11434"
            selectByMouse: true
        }

        Label {
            text: qsTr("Model")
        }

        TextField { 
            id: modelNameField
            Layout.fillWidth: true
            placeholderText: "qwen3-vl:2b-instruct-q8_0"
        }

        Label {
            text: qsTr("Current prompt")
        }

        RowLayout {
            Layout.fillWidth: true

            TextField {
                id: promptNameField
                readOnly: true
                Layout.fillWidth: true
                placeholderText: "Default"
            }

            Button {
                text: qsTr("Set")
                enabled: promptsCombo.currentIndex >= 0

                onClicked: {
                    promptNameField.text = promptsCombo.currentText
                }
            }
        }


        // Label {
        //     text: qsTr("Prompt Name")
        // }

        // TextField { 
        //     id: promptNameField
        //     Layout.fillWidth: true
        //     placeholderText: "Default"
        // }

        Label {
            text: qsTr("Prompts")
        }

        ComboBox {
            id: promptsCombo

            // model: ListModel {
            //     id: model
            //     ListElement { text: "Banana" }
            //     ListElement { text: "Apple" }
            //     ListElement { text: "Coconut" }
            // }

            model: root.settingsStore.prompts
            textRole: "name"
            editable: false
            onAccepted: {
                if (find(editText) === -1)
                    model.append({text: editText})
            }

            onActivated: {
                console.log('Activated: ' + editText)
                console.log('Current index: ' + currentIndex)
            }

        }

        ScrollView {
            id: view
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumHeight: 100

            contentWidth: availableWidth

            ScrollBar.vertical.policy: ScrollBar.AsNeeded
            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

            TextArea {
                id: promptValueField
                
                font: root.settingsStore.fixedFont

                width: view.availableWidth
                wrapMode: TextEdit.Wrap
                text: {
                    const prompts = root.settingsStore.prompts
                    const index = promptsCombo.currentIndex

                    if (index <0 || index >= prompts.length)
                        return ""
                    return prompts[index].value
                }

                onTextChanged: {
                    if (activeFocus && promptsCombo.currentIndex >= 0) {
                        root.settingsStore.updatePromptValue(
                            promptsCombo.currentIndex,
                            text
                        )
                    }
                }
            }
        }
    }

    onOpened: {
        ollamaUrlField.text = root.settingsStore.ollamaUrl
        modelNameField.text = root.settingsStore.modelName
        promptNameField.text = root.settingsStore.promptName
        const index = promptsCombo.find(root.settingsStore.promptName)
        promptsCombo.currentIndex = index >=0 ? index : (promptsCombo.count > 0 ? 0 : -1)
    }

    onAccepted: {
        root.settingsStore.save(ollamaUrlField.text, modelNameField.text, promptNameField.text)
    }

    onRejected: {
        console.log("Settings cancelled")
    }
}
