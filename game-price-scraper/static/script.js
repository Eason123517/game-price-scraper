document.addEventListener('DOMContentLoaded', function() {
    const gameInput = document.getElementById('gameInput');
    const searchBtn = document.getElementById('searchBtn');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    
    searchBtn.addEventListener('click', performSearch);
    gameInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
    
    async function performSearch() {
        const gameName = gameInput.value.trim();
        
        if (!gameName) {
            alert('請輸入遊戲名稱');
            return;
        }
        
        // 顯示載入中
        loading.classList.remove('hidden');
        results.innerHTML = '';
        searchBtn.disabled = true;
        searchBtn.textContent = '搜尋中...';
        
        try {
            const response = await fetch('/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ game_name: gameName })
            });
            
            const data = await response.json();
            
            if (data.success) {
                displayResults(data.results, data.count);
            } else {
                throw new Error(data.error || '搜尋失敗');
            }
            
        } catch (error) {
            console.error('搜尋錯誤:', error);
            results.innerHTML = `<div class="error">搜尋過程中發生錯誤: ${error.message}</div>`;
        } finally {
            loading.classList.add('hidden');
            searchBtn.disabled = false;
            searchBtn.textContent = '🔍 搜尋';
        }
    }
    
    function displayResults(listings, count) {
        if (count === 0) {
            results.innerHTML = '<div class="no-results">沒有找到任何結果</div>';
            return;
        }
        
        const resultsHtml = listings.map(listing => `
            <div class="result-card">
                <div class="result-header">
                    <div class="result-title">${listing.title}</div>
                    <div class="result-price">$${listing.price.toLocaleString()}</div>
                </div>
                <div class="result-meta">
                    <span><strong>平台:</strong> ${listing.platform}</span>
                    <span><strong>狀況:</strong> ${listing.condition}</span>
                    <span><strong>地點:</strong> ${listing.location}</span>
                </div>
                <div class="result-footer">
                    <span class="result-source">${listing.source}</span>
                    ${listing.url ? `<a href="${listing.url}" target="_blank">查看商品</a>` : ''}
                </div>
            </div>
        `).join('');
        
        results.innerHTML = `
            <div class="results-header">
                <h3>找到 ${count} 個結果 (按價格排序)</h3>
            </div>
            ${resultsHtml}
        `;
    }
});