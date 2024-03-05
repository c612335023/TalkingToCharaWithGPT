# [ChatGPT](https://chat.openai.com/)と[Style-Bert-VITS2](https://github.com/litagin02/Style-Bert-VITS2)によるキャラクターとの会話
このプロジェクトは、[ChatGPT](https://chat.openai.com/)にキャラクターの人格を付与し、出力内容を[Style-Bert-VITS2](https://github.com/litagin02/Style-Bert-VITS2)を用いてキャラクターの声を学習したモデルを使って音声化することで、まるでキャラクターと会話しているかのような気分を味わえるものです。
## 人格付与プロンプト
キャラクターの人格を設定するためには、[ChatGPT用キャラ口調設定Wiki](https://seesaawiki.jp/chatgpt_char_prompt/)を参考にしたプロンプトを使用します。
## 実行方法
1. [Style-Bert-VITS2](https://github.com/litagin02/Style-Bert-VITS2)を用いてモデルを学習
1. prompt.txtに[ChatGPT用キャラ口調設定Wiki](https://seesaawiki.jp/chatgpt_char_prompt/)を参考にしたプロンプトを入力
1. `talk.py`の`MODEL_NAME`(1.で作成したモデルのパス)と`SESSION_TOKEN`([UnlimitedGPT](https://github.com/Sxvxgee/UnlimitedGPT)のセッショントークン)を入力
1. `talk.py`を実行
## 使用方法
1. 「呼ばれ方」と「呼び方」を入力
1. [ChatGPT](https://chat.openai.com/)により、人格付与プロンプトに応じた応答が生成され、音声が再生される
1. 応答への返信を入力する
1. 応答が音声化され再生される
1. `!exit`により終了
## 依存関係
このプロジェクトは以下の依存関係に依存しています：
- [UnlimitedGPT](https://github.com/Sxvxgee/UnlimitedGPT): テキスト生成に使用されるGPTモデルです。
- Sounddevice: 音声の再生に使用されます。
## 今後の予定（やる気があれば）
- GUIの実装
- 音声認識の実装（テキストの入力ではなく、マイクに向かって喋った内容を入力できるようにする）