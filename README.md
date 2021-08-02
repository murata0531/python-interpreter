# docker-python

コンテナ立ち上げ

```
$ docker-compose up -d --build
```

コンテナとイメージ破棄

```
$ docker-compose down --rmi all --volumes --remove-orphans
```

コンテナにアタッチ

```
$ docker-compose exec python3 bash
```

python 実行(例としてsample.pyを実行する)

```
$ python sample.py 180.0
```

コンテナ削除

```
$ docker-compose down
```

コンテナ再起動

```
$ docker-compose up -d
```

# Jupyter Notebookを使用する

コンテナ内に入らずイメージだけ作成

```
$ docker-compose build
```

イメージ確認

```
$ docker images
```
Jupyter Notebookを起動

```
$ docker run -v $PWD/opt:/root/opt -w /root/opt -it --rm -p 7777:8888 docker-python_python3 jupyter-lab --ip 0.0.0.0 --allow-root -b localhost
```

↓下記のようなメッセージが表示されたら正常起動↓

```
To access the server, open this file in a browser:
        file:///root/.local/share/jupyter/runtime/jpserver-1-open.html
    Or copy and paste one of these URLs:
        http://46102976db71:8888/lab?token=xxxxxxxxxx
        http://127.0.0.1:8888/lab?token=xxxxxxxxxx
 ```
 
 ブラウザで `http://127.0.0.1:7777` にアクセス(今回はポート番号7777にしているが、特に指定はない)
 
 Token authentication is enabledというページが出るので、そこに上のメッセージでtoken=に続くコードをコピーしてPassword or tokenの入力欄に入力してLog inボタンを押す
