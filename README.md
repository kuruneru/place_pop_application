# post_sightseeing application

## 以下に仕様と技術を記す

- 仕様
    - まず，このWebアプリは観光名所を投稿するアプリである．

    - メインページでは絞り込み等を行えるようにし，別のページで**会員登録**，**投稿**を行えるようにする．それぞれの仕様についてはいかに示す．

        - 会員登録
            - 会員登録の際には，以下の情報を必ず入力することとする．
            
                | 名前  | メールアドレス  | パスワード  |
                |:---:|:---:|:---:|
                | example  | info@example.com  | example  |

        - 投稿
            - 投稿する際に以下の情報を必ず入力するkととする．．

                | 場所  | 名前  | 住所  | 画像  | コメント  |
                |:---:|:---:|:---:|:---:|:---:|
                | example  | example  | example  | example  | example  |
        - アプリの使い方
            - このアプリは以下の機能を備えている

- 技術
    - Render: Webページの公開
    - Neon: SQL
    - FastAPI: Webアプリ用
    - Docker: Renderでアプリを開くための初期設定
