
# 投稿アプリ データベース設計案


## users テーブル (ユーザー情報)

- id: INT, PRIMARY KEY, AUTO_INCREMENT
  (ユーザーID)
- username: VARCHAR
  (ユーザー名)
- email: VARCHAR, UNIQUE
  (メールアドレス)
- password_hash: VARCHAR
  (ハッシュ化されたパスワード)
- profile: TEXT
  (自己紹介文)
- created_at: TIMESTAMP
  (作成日時)
- updated_at: TIMESTAMP
  (更新日時)


## posts テーブル (投稿情報)

- id: INT, PRIMARY KEY, AUTO_INCREMENT
  (投稿ID)
- user_id: INT, FOREIGN KEY (references users.id)
  (投稿者のID)
- title: VARCHAR
  (タイトル)
- place_name: VARCHAR
  (場所の名前)
- address: VARCHAR
  (住所)
- image_url: VARCHAR
  (画像へのURL)
- created_at: TIMESTAMP
  (作成日時)
- updated_at: TIMESTAMP
  (更新日時)


## comments テーブル (コメント情報)

- id: INT, PRIMARY KEY, AUTO_INCREMENT
  (コメントID)
- post_id: INT, FOREIGN KEY (references posts.id)
  (投稿ID)
- user_id: INT, FOREIGN KEY (references users.id)
  (コメント投稿者のID)
- content: TEXT
  (コメント本文)
- created_at: TIMESTAMP
  (作成日時)
- updated_at: TIMESTAMP
  (更新日時)


## post_evaluations テーブル (投稿への評価情報)

- id: INT, PRIMARY KEY, AUTO_INCREMENT
  (評価ID)
- post_id: INT, FOREIGN KEY (references posts.id)
  (投稿ID)
- user_id: INT, FOREIGN KEY (references users.id)
  (評価したユーザーのID)
- evaluation_type: INT
  (評価の種類。例: 1=いいね, -1=よくないね)
- created_at: TIMESTAMP
  (作成日時)

-- Constraints <br>
-- UNIQUE KEY on (post_id, user_id) to prevent multiple evaluations. <br>
-- (post_idとuser_idの組み合わせにUNIQUE制約をかけ、多重評価を防ぐ) <br>