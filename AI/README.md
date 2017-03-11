# RoboFish

AI of RoboFish

#### lstm_deepfishing.py,lstm_deepfishing.ipynb
学習データ(csv)から魚が釣れるか判定する学習モデル(チェックポイント)を作成するプログラムです  
すでに5万ステップで学習したモデルが`ckptdir-sqrt5`のディレクトリ先に用意されています

#### fishing_test.ipynb
作成した学習モデルでRaspberryPiに繋げた釣り竿から加速度のデータをとり、魚の引きの判定を行うプログラムです
