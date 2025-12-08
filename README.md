# Document Editing, do not use
- 
- 
- 

<p align="center">
  <img src="assets/icon.png" width = "200" height = "200"/>
</p>
<h1 align="center">TuneZ</h1>

<p align="center">
一個基於 Python，每個需要在 Discord 播放音樂的人都可以<strong>開箱即用</strong>的 Discord bot。
</p>

## 前言
<details>
    <summary>為什麼要做這個?</summary>
    <ul>
        <li>
            前陣子有個朋友跟我要了<a href="https://github.com/NotKeKe/Discord-Bot-YinXi">音汐</a>，我後來看了<a href="https://yeecord.com/">YEE式機器龍</a>的<a href="https://yeecord.com/blog/thats-why-i-gave-up-on-music">貼文</a>後才知道，原來現在的音樂機器人已經困難成這樣了
        </li>
        <li>
            又因為我其實原本就有音汐了，我就想著 我如果把他關於音樂的代碼專門分出來 做音樂機器人，<del>會不會火</del>
        </li>
        <li>
            何況現在 yt-dlp 如果一直從同一個 ip 發送請求的話，也很容易出現 403(沒有權限)或者其他錯誤的請求 <del>(這大概也是為什麼音樂機器人越來越少的原因，畢竟穩定的來源確實滿難找的)</del><br>
            但如果每個使用者都只是根據自己的需求 去自架 discord bot，是不是就可以解決這個問題
        </li>
        <li>
            所以說我就做了這個 TuneZ
        </li>
    </ul>
</details>
<details>
    <summary>為什麼叫 TuneZ</summary>
    <ul>
        <li>
            其實原因超簡單
        </li>
        <li>
            我先隨便讓Copilot幫我想個名字，出現了 Tune。 <br>
            後來想想，大約2000年左右的人都會被稱作 Z 世代 <br>
            所以又出現了 Z <br>
            節合起來就變成 <strong>TuneZ</strong> 了
        </li>
    </ul>
</details>
<details>
    <summary>會不會有風險?</summary>
    <ul>
        <li>
            答案其實也很簡單 自己使用就不會有
        </li>
        <li>
            這種東西通常自己 或者讓朋友用一下都不會出啥事
        </li>
        <li>
            除非你選擇把他拿去營利 <br>
            那就不能怪我了:) <br>
            我沒考慮負責
        </li>
    </ul>
</details>

## 使用
1. 如果你只是單純希望有一個 discord 音樂機器人，可以直接邀請[音汐](https://github.com/NotKeKe/Discord-Bot-YinXi)進你的群，這也是我最早開始做的專案。
    - [邀請連結](https://discord.com/oauth2/authorize?client_id=990798785489825813)
2. 自架 ~~(既然你都點進這個專案了 應該也會選擇這個吧)~~ <br>
    **❗如果你還沒有 discord bot，先前往[這個檔案](assets/docs//Register_Discord_Bot.md)去看教學❗**

    1. Windows
        <details>
            <summary>使用 .exe</summary>
            <ul>
                <li>
                    前往 <a href="https://github.com/NotKeKe/easy-discord-music-bot/releases">Release</a>，下載適合你的版本 (現在應該只有 .exe)
                </li>
                <li>
                    執行他之後，正常來說會先被關閉，因為他只是要複製必要資源出去。
                </li>
                <li>
                    前往 Roaming 目錄，通常應該會是這樣的格式 (把 USERNAME 改成你自己的 應該就可以找到)
                    <code>C:\Users\USERNAME\AppData\Roaming\Easy Music Bot</code>
                </li>
                <li>
                    找到 .env，並使用任何你喜歡的文字編輯器打開
                </li>
                <li>
                    把你剛剛在 Discord Developer 網站裡面創建的 Bot 的 Token 貼到 DISCORD_TOKEN，結果應該像這樣
                    <pre><code class="lang-text"><span class="hljs-attr">DISCORD_TOKEN</span> = MTQ0Nz.....<br><span class="hljs-attr">OWNER_ID</span> = OWNER_ID</code></pre>
                </li>
                <li>
                    
                </li>
            </ul>
        </details>
    2. Linux
        - 尚未測試