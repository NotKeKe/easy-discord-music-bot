<p align="center">
  <img src="assets/icon.png" width = "200" height = "200"/>
</p>
<h1 align="center">TuneZ</h1>

<p align="center">
一個基於 Python，每個需要在 Discord 播放音樂的人都可以<strong>開箱即用</strong>的 Discord bot。
</p>

## 📖 前言
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

## 🖥️ Demo
TuneZ 有支援中文，只是因為我的 Discord 預設語言是英文，所以他顯示英文
![Demo](assets/docs/demo.png)

## 🌟 特色
<details><summary><strong>自帶淺藍色動畫 emojis</strong></summary></details>
<details>
    <summary><strong>可自訂 emojis</strong></summary>
    <strong>❗注意圖片檔名(不含後綴) 要與 <a href="assets/emojis/">assets/emojis</a> 裡面的檔名一樣❗</strong> <small>例如: <code>list.gif</code> → <code>list.png</code></small>
    <ul>
        <li>
            在 Windows 當中，進到 <small><code>C:\Users\USERNAME\AppData\Roaming\Easy Music Bot\data\emojis</code></small> 可以自己放圖片上去
        </li>
        <li>
            在其他環境下，可在 <code>./data/emojis/</code> 中上傳自定義圖片
        </li>
        <li><strong>
            最後在 Discord 頻道裡面 使用 <code>/reload_emojis</code> 來重載 emojis
        </strong></li>
    </ul>
</details>
<details>
    <summary><strong>簡單易上手</strong></summary>
    <ul>
        <li>
            <strong>Windows 用戶</strong>可直接透過 .exe 檔開啟 TuneZ
        </li>
        <li>
            其他環境的用戶，也可以直接使用 <strong>Docker</strong> 啟動
        </li>
        <li>
            或是在安裝好依賴後，直接運行 <code>main.py</code>
        </li>
    </ul>
</details>


## 🛠️ 使用
### 1. 如果你只是單純希望有一個 Discord 音樂機器人，可以直接邀請[音汐](https://github.com/NotKeKe/Discord-Bot-YinXi)進你的群，這也是我最早開始做的專案。
- [邀請連結](https://discord.com/oauth2/authorize?client_id=990798785489825813)
### 2. 自架 ~~(既然你都點進這個專案了 應該也會選擇這個吧)~~ <br>
**❗如果你還沒有 Discord Bot，先前往[這個檔案](assets/docs//Register_Discord_Bot.md)去看教學❗**

**❗除了使用 .exe 以外，其他方法暫時都需要先 克隆/下載該專案❗** <br>
<small>`git clone https://github.com/NotKeKe/TuneZ-Discord-Bot.git`</small>

-  Windows
    <details>
        <summary>使用 .exe</summary>
        <ul>
            <li>
                <strong>前往 <a href="https://github.com/NotKeKe/easy-discord-music-bot/releases">Release</a>，下載適合你的版本 (現在應該只有 .exe)</strong>
            </li>
            <li>
                <strong>執行 <code>windows.exe</code> <br></strong>
                執行之後，正常來說會先被關閉，因為他只是要複製必要資源出去。
            </li>
            <li>
                <strong>前往 Roaming 目錄</strong> <br>
                通常應該會是這樣的格式 (把 USERNAME 改成你自己的 應該就可以找到)
                <small><code>C:\Users\USERNAME\AppData\Roaming\Easy Music Bot</code></small>
            </li>
            <li>
                <strong>找到 <code>.env</code>，並使用任何你喜歡的文字編輯器打開</strong>
            </li>
            <li>
                <strong>輸入 DISCORD_TOKEN</strong> <br>
                把你剛剛在 Discord Developer 網站裡面創建的 Bot 的 Token 貼到 DISCORD_TOKEN，結果應該像這樣
                <pre><code class="lang-text"><span class="hljs-attr">DISCORD_TOKEN</span> = MTQ0Nz.....<br><span class="hljs-attr">OWNER_ID</span> = OWNER_ID</code></pre>
                <small>(OWNER_ID 就是你自己的 Discord ID，每個使用者的都不一樣，像我的就是 7038778.....，就算不填也沒關係，目前只有在需要 reload_emojis 的時候才會用到)</small>
            </li>
            <li>
                <strong>重新開啟 <code>windows.exe</code></strong>
            </li>
        </ul>
        現在 你應該可以看到他正常啟動了<br>
        <strong>用 /play 來開始播放音樂吧</strong>
        <img src="assets/docs/opened_bot.png">
    </details>

- [Docker](https://www.docker.com/)
    <details>
        <summary>Docker Compose</summary>
        <ul>
            <li>
                將 <code>.env.example</code> 重命名為 <code>.env</code>
                <pre><code class="lang-bash"><span class="hljs-selector-tag">cp</span> <span class="hljs-selector-class">.env</span><span class="hljs-selector-class">.example</span> <span class="hljs-selector-class">.env</span></code></pre>
            </li>
            <li>
                填入你自己的 Discord Bot Token <br>
                大概像這樣
                <pre><code class="lang-env"><span class="hljs-attr">DISCORD_TOKEN</span> = MTQ0Nz.....<br><span class="hljs-attr">OWNER_ID</span> = OWNER_ID</code></pre>
                <small>(OWNER_ID 就是你自己的 Discord ID，每個使用者的都不一樣，像我的就是 7038778.....，就算不填也沒關係，目前只有在需要 reload_emojis 的時候才會用到)</small>
            </li>
            <li>
                創建 logs 和 data 目錄 <br>
                (logs 主要用於查看錯誤，data 用於儲存使用者自訂播放清單、url 暫存等等......)
                <pre><code class="lang-bash"><span class="hljs-title">mkdir</span> -p <span class="hljs-class"><span class="hljs-keyword">data</span> logs</span></code></pre>
            </li>
            <li>
                使用 docker compose 啟動
                <pre><code class="lang-bash">docker compose up <span class="hljs-_">-d</span></code></pre>
            </li>
        </ul>
        <strong>Bot 應該就會成功開起來了!</strong>
    </details>
    
- [uv](https://github.com/astral-sh/uv)
    <details>
        <summary>本專案基於 uv 來管理項目依賴及虛擬環境 (venv)，因此在這裡推薦一下 uv</summary>
        <ul>
            <li>
                安裝 uv (從以下方法 選一個最適合你的)
                <ul>
                    <li>
                        使用 pip: <pre><code class="lang-bash">pip <span class="hljs-keyword">install</span> uv</code></pre>
                    </li>
                    <li>
                        Windows: <pre><code class="lang-bash"><span class="hljs-symbol">powershell</span> -ExecutionPolicy <span class="hljs-keyword">ByPass </span>-c <span class="hljs-string">"irm https://astral.sh/uv/install.ps1 | iex"</span></code></pre>
                    </li>
                    <li>
                        macOS or Linux: <pre><code class="lang-bash">curl -LsSf http<span class="hljs-variable">s:</span>//astral.<span class="hljs-keyword">sh</span>/uv/install.<span class="hljs-keyword">sh</span> | <span class="hljs-keyword">sh</span></code></pre>
                    </li>
                    <li>
                        更多方法請前往 <a href="https://docs.astral.sh/uv/getting-started/installation/#standalone-installer">uv官網</a>
                    </li>
                </ul>
            </li>
            <li>
                將 <code>.env.example</code> 重命名為 <code>.env</code>
            </li>
            <li>
                在 <code>.env</code> 中，填入你的 Token <br>
                大概像這樣
                <pre><code class="lang-env"><span class="hljs-attr">DISCORD_TOKEN</span> = MTQ0Nz.....<br><span class="hljs-attr">OWNER_ID</span> = OWNER_ID</code></pre>
                <small>(OWNER_ID 就是你自己的 Discord ID，每個使用者的都不一樣，像我的就是 7038778.....，就算不填也沒關係，目前只有在需要 reload_emojis 的時候才會用到)</small>
            </li>
            <li>
                同步虛擬環境
                <pre><code class="lang-bash">uv <span class="hljs-keyword">sync</span></code></pre>
            </li>
            <li>
                執行程式
                <pre><code class="lang-bash">uv <span class="hljs-keyword">run</span><span class="bash"> main.py</span></code></pre>
            </li>
        </ul>
    </details>