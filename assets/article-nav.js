// 文章導航：根據分類自動更新「回到[主題]」連結
(function () {
  var categoryMap = {
    'materials': { name: '原料與價格', file: 'materials.html' },
    'mills': { name: '全球鋼廠動態', file: 'mills.html' },
    'vehicles': { name: '先進載具與鋼材', file: 'vehicles.html' },
    'demand': { name: '下游需求觀察', file: 'demand.html' },
    'trade': { name: '貿易與政策', file: 'trade.html' },
    'carbon': { name: '碳中和', file: 'carbon.html' },
    'decarb': { name: '低碳冶金', file: 'decarb.html' },
    'steel101': { name: '鋼鐵小學堂', file: 'steel101.html' },
    'csc': { name: '中鋼新聞專區', file: 'csc.html' }
  };

  // 嘗試從文章的 data-category 屬性或其他來源獲取分類
  function getArticleCategory() {
    // 優先級 1: 檢查 article 元素的 data-category
    var article = document.querySelector('article');
    if (article && article.dataset.category) {
      return article.dataset.category;
    }

    // 優先級 2: 檢查全局變數
    if (typeof window.ARTICLE_CATEGORY !== 'undefined') {
      return window.ARTICLE_CATEGORY;
    }

    // 優先級 3: 從 articles.json 查詢（基於 URL）
    var currentPath = window.location.pathname;
    var match = currentPath.match(/\/articles\/([^/]+)\.html/);
    if (match) {
      var articleId = match[1];
      // 需要從 articles.json 中查詢
      return fetch('../../data/articles.json?ts=' + Date.now(), { cache: 'no-store' })
        .then(function (r) { return r.json(); })
        .then(function (d) {
          var item = (d.items || []).find(function (a) { return a.id === articleId; });
          return item ? item.category : null;
        })
        .catch(function () { return null; });
    }

    return null;
  }

  function updateNavigation(category) {
    if (!category || !categoryMap[category]) return;

    var info = categoryMap[category];
    var navLink = document.querySelector('main > p:last-of-type > a');

    if (navLink) {
      navLink.href = '../' + info.file;
      navLink.textContent = '← 回到' + info.name;
    }
  }

  // 處理同步和非同步的分類獲取
  var category = getArticleCategory();
  if (category && typeof category === 'string') {
    updateNavigation(category);
  } else if (category && typeof category.then === 'function') {
    category.then(function (cat) { updateNavigation(cat); });
  }
})();
