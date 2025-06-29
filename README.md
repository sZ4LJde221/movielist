# Filmarks 映画リスト - index.html 解説

## 概要
このHTMLファイルは、Filmarksから取得した映画データを表示するWebアプリケーションです。GitHubのAPIを使用してJSONファイルを取得し、映画情報をカード形式で表示します。

## ファイル構造

### HTML部分
```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <!-- メタ情報とTailwind CSSの読み込み -->
</head>
<body>
  <!-- メインコンテンツ -->
</body>
</html>
```

### 主要な要素
- **データ選択**: JSONファイルを選択するドロップダウン
- **ソート機能**: タイトル、評価、日付順でソート
- **ページネーション**: 大量のデータを分割表示
- **映画カード**: 各映画の情報を表示

## JavaScriptコード解説

### 1. 定数と変数の定義

```javascript
// 設定のキャッシュキー（ローカルストレージに保存する設定項目）
const CACHE_KEYS = ['jsonSelect','sortField','sortDir','pageSize'];

// GitHubリポジトリ情報
const owner = 'sz4ljde221';    // GitHubユーザー名
const repo  = 'movielist';     // リポジトリ名
const dataPath = 'data';       // データファイルのパス

// グローバル変数
let movies = [];               // 映画データの配列
let currentPage = 1;           // 現在のページ番号
```

### 2. ページ読み込み時の処理

```javascript
document.addEventListener('DOMContentLoaded', ()=>{
  // 前回の設定をローカルストレージから復元
  CACHE_KEYS.forEach(key=>{
    const val = localStorage.getItem(key);
    if(val && document.getElementById(key)) 
      document.getElementById(key).value = val;
  });
});
```

**解説**:
- `DOMContentLoaded`: HTMLの読み込みが完了した時に実行
- `localStorage.getItem()`: ブラウザに保存された設定を取得
- `forEach()`: 配列の各要素に対して処理を実行

### 3. GitHub APIからのファイル一覧取得

```javascript
fetch(`https://api.github.com/repos/${owner}/${repo}/contents/${dataPath}`)
  .then(res=>res.json())
  .then(files=>{
    // JSONファイルのみをフィルタリング
    const jsonFiles = files.filter(f=>f.type==='file'&&f.name.endsWith('.json'))
                          .map(f=>f.name)
                          .sort((a,b)=>(a<b?1:-1));
    
    // セレクトボックスにオプションを追加
    const sel=document.getElementById('jsonSelect');
    sel.innerHTML = jsonFiles.map(n=>`<option value="${n}">${n}</option>`).join('');
    
    // 最初のファイルを読み込み
    loadData(jsonFiles[0]);
  }).catch(err=>console.error('GitHub API読み込み失敗',err));
```

**解説**:
- `fetch()`: HTTPリクエストを送信
- `.then()`: 非同期処理の結果を受け取る
- `.filter()`: 条件に合う要素のみを抽出
- `.map()`: 配列の各要素を変換
- `.sort()`: 配列をソート（新しい順）

### 4. イベントハンドラーの設定

```javascript
// ファイル選択時の処理
document.getElementById('jsonSelect').onchange = e=>{
  currentPage=1;  // ページを1にリセット
  loadData(e.target.value);  // 選択されたファイルを読み込み
};

// 適用ボタンクリック時の処理
document.getElementById('apply').onclick = ()=>{
  currentPage=1;  // ページを1にリセット
  render();       // 画面を再描画
};
```

### 5. データ読み込み関数

```javascript
function loadData(filename){
  fetch(`${dataPath}/${filename}`)
    .then(res=>res.json())
    .then(data=>{
      // データ形式を統一（配列またはオブジェクト）
      movies=Array.isArray(data)?data:(data.movies||[]);
      render();  // 画面を描画
    })
    .catch(err=>console.error(`${filename}読み込み失敗`,err));
}
```

**解説**:
- `Array.isArray()`: 配列かどうかを判定
- `data.movies||[]`: moviesプロパティがない場合は空配列を使用

### 6. メイン描画関数

```javascript
function render(){
  // 設定値を取得
  const field = document.getElementById('sortField').value;  // ソート項目
  const dir   = document.getElementById('sortDir').value;    // ソート方向
  const size  = +document.getElementById('pageSize').value;  // 表示件数
  
  // ソート処理
  let sorted;
  if(field==='original') {
    sorted = movies.slice();  // 元の順序を保持
  } else {
    sorted = movies.slice().sort((a,b)=>{
      let v1=field==='rating'?+(a[field]||0):(a[field]||'').toLowerCase();
      let v2=field==='rating'?+(b[field]||0):(b[field]||'').toLowerCase();
      return (v1>v2?1:(v1<v2?-1:0))*(dir==='asc'?1:-1);
    });
  }
  
  // ページネーション計算
  const total = sorted.length;
  const pages=Math.ceil(total/size);
  currentPage = Math.min(currentPage,pages)||1;
  const start=(currentPage-1)*size;
  const items=sorted.slice(start,start+size);
  
  // カード生成とページネーション生成
  // ...
}
```

**解説**:
- `+`演算子: 文字列を数値に変換
- `||0`: 値がfalsyの場合は0を使用
- `toLowerCase()`: 文字列を小文字に変換
- `Math.ceil()`: 切り上げ
- `Math.min()`: 最小値を取得
- `slice()`: 配列の一部を切り出し

### 7. カード生成

```javascript
const grid=document.getElementById('grid');
grid.innerHTML = items.map(item=>`
  <div class="bg-white rounded-lg overflow-hidden shadow hover:shadow-lg transition">
    <a href="${item.link}" target="_blank">
      <img loading="lazy" src="${item.image_url?item.image_url:'image/noimage.png'}" alt="${item.title}" class="w-full h-48 object-cover">
    </a>
    <div class="p-4 flex flex-col h-40">
      <a href="${item.link}" target="_blank" class="text-lg font-semibold text-gray-900 hover:text-indigo-600 mb-2 truncate">${item.title}</a>
      <div class="mt-auto text-indigo-500 font-medium">評価: ${item.rating||'-'}</div>
    </div>
  </div>`).join('');
```

**解説**:
- テンプレートリテラル（バッククォート）: 文字列内に変数を埋め込み
- `loading="lazy"`: 画像の遅延読み込み
- `target="_blank"`: 新しいタブでリンクを開く
- `truncate`: テキストを省略表示

### 8. ページネーション生成

```javascript
function createPagination(containerId){
  const pg=document.getElementById(containerId);
  pg.innerHTML='';
  
  function btn(i,label){
    const b=document.createElement('button');
    b.textContent=label||i;
    b.className=`px-3 py-1 rounded-md ${i===currentPage?'bg-indigo-600 text-white':'bg-white text-gray-700 border border-gray-300'}`;
    if(i!==currentPage) {
      b.onclick=()=>{
        currentPage=i;
        render();
        window.scrollTo({top:0,behavior:'smooth'});
      };
    } else {
      b.disabled=true;
    }
    return b;
  }
  
  // ページネーションの表示ロジック
  // ...
}
```

**解説**:
- `document.createElement()`: HTML要素を作成
- `textContent`: テキスト内容を設定
- `className`: CSSクラスを設定
- `window.scrollTo()`: ページの特定位置にスクロール

## 修正・改修時の考慮点

### 1. エラーハンドリング
- 現在のエラーハンドリングは基本的なもの
- ユーザーフレンドリーなエラーメッセージの表示を検討
- ネットワークエラー時の再試行機能

### 2. パフォーマンス
- 大量のデータ処理時の最適化
- 画像の遅延読み込み（既に実装済み）
- 仮想スクロールの検討

### 3. ユーザビリティ
- ローディング表示の追加
- 検索機能の実装
- フィルタリング機能の追加

### 4. セキュリティ
- XSS攻撃対策（現在は基本的な対策済み）
- 入力値の検証強化

### 5. 保守性
- コードの分割（モジュール化）
- 定数の外部化
- コメントの充実

## よく使われるJavaScript構文

### アロー関数
```javascript
// 従来の関数
function add(a, b) {
  return a + b;
}

// アロー関数
const add = (a, b) => a + b;
```

### テンプレートリテラル
```javascript
const name = "太郎";
const message = `こんにちは、${name}さん！`;
```

### 分割代入
```javascript
const { title, rating } = movie;
```

### 三項演算子
```javascript
const result = condition ? value1 : value2;
```

### 論理演算子
```javascript
const value = data || defaultValue;  // デフォルト値
const result = data && data.property;  // 安全なプロパティアクセス
```

## 学習の次のステップ

1. **ES6+の機能**: アロー関数、テンプレートリテラル、分割代入
2. **非同期処理**: Promise、async/await
3. **DOM操作**: 要素の作成、削除、属性変更
4. **イベント処理**: クリック、フォーム送信、キーボード入力
5. **ローカルストレージ**: データの永続化
6. **API連携**: fetch、JSON処理
7. **エラーハンドリング**: try-catch、エラー表示 