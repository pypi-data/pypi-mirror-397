def delicious_pasta():
    taste = input("どんな？: ")
    food = input("何を?: ")
    do = input("どうした？: ")
    who = input("誰が？: ")
    lyric = taste + food + do + who
    print(lyric)
    if lyric == "おいしいパスタ作ったお前":
        print("家庭的な女がタイプの俺一目惚れ")
    else:
        print("純恋歌で検索")