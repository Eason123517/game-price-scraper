document.addEventListener('DOMContentLoaded', function() {
    const gameInput = document.getElementById('gameInput');
    const searchBtn = document.getElementById('searchBtn');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    
    // 搜尋建議列表
    const searchSuggestions = [
        '薩爾達傳說 王國之淚',
        '超級瑪利歐兄弟 驚奇',
        '寶可夢 朱紫',
        'FIFA 24',
        '戰神',
        '最後生還者',
        '血源詛咒',
        '魔物獵人 崛起'
    ];
    
    // 綁定事件
    searchBtn.addEventListener('click', performSearch);
    gameInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
    
    // 輸入提示
    gameInput.addEventListener('input', function() {
        const value = this.value.toLowerCase();
        // 這裡可以加入搜尋建議功能
    });
    
    // 載入支援的平台
    loadSupportedPlatforms();
    
    async function performSearch() {
        const gameName = gameInput.value.trim();
        
        if (!gameName) {
            showError('請輸入遊戲名稱');
            gameInput.focus();
            return;
        }
        
        if (gameName.length < 2) {
            showError('遊戲名稱至少需要2個字元');
            gameInput.focus();
            return;
        }
        
        // 顯示載入狀態
        setLoadingState(true);
        
        try {
            const response = await fetch('/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ game_name: gameName }),
                // 增加超時時間，因為真實搜尋需要更多時間
                signal: AbortSignal.timeout(60000) // 60秒超時
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                displayResults(data.results, data.count, data.search_term);
            } else {
                throw new Error(data.error || '搜尋失敗');
            }
            
        } catch (error) {
            console.error('搜尋錯誤:', error);
            
            if (error.name === 'AbortError') {
                showError('搜尋超時，請稍後再試');
            } else if (error.message.includes('NetworkError') || error.message.includes('Failed to fetch')) {
                showError('網路連線有問題，請檢查您的網路連線');
            } else {
                showError(`搜尋過程中發生錯誤: ${error.message}`);
            }
        } finally {
            setLoadingState(false);
        }
    }
    
    function setLoadingState(isLoading) {
        if (isLoading) {
            loading.classList.remove('hidden');
            results.innerHTML = '';
            searchBtn.disabled = true;
            searchBtn.textContent = '搜尋中...';
            gameInput.disabled = true;
        } else {
            loading.classList.add('hidden');
            searchBtn.disabled = false;
            searchBtn.textContent = '🔍 搜尋';
            gameInput.disabled = false;
        }
    }
    
    function displayResults(listings, count, searchTerm) {
        if (count === 0) {
            results.innerHTML = `
                <div class="no-results">
                    <h3>沒有找到「${searchTerm}」的結果</h3>
                    <p>建議：</p>
                    <ul>
                        <li>檢查遊戲名稱拼寫</li>
                        <li>嘗試使用遊戲的簡稱或英文名</li>
                        <li>去掉版本號或平台名稱</li>
                    </ul>
                </div>`;
            return;
        }
        
        // 按平台分組
        const groupedResults = groupByPlatform(listings);
        
        const resultsHtml = listings.map((listing, index) => `
            <div class="result-card" data-index="${index}">
                <div class="result-header">
                    <div class="result-title" title="${listing.title}">${truncateTitle(listing.title, 60)}</div>
                    <div class="result-price">$${listing.price.toLocaleString()}</div>
                </div>
                <div class="result-meta">
                    <span class="platform-badge platform-${listing.platform.toLowerCase().replace(/[^a-z0-9]/g, '')}">${listing.platform}</span>
                    <span class="condition-badge condition-${listing.condition}">${listing.condition}</span>
                    <span class="location">📍 ${listing.location}</span>
                </div>
                <div class="result-footer">
                    <span class="result-source">${listing.source}</span>
                    <div class="result-actions">
                        ${listing.url ? `<a href="${listing.url}" target="_blank" rel="noopener noreferrer" class="view-link">查看商品 ↗</a>` : ''}
                        <button class="compare-btn" onclick="toggleCompare(${index})">比較</button>
                    </div>
                </div>
            </div>
        `).join('');
        
        // 價格統計
        const priceStats = calculatePriceStats(listings);
        
        results.innerHTML = `
            <div class="results-header">
                <h3>「${searchTerm}」搜尋結果 (${count} 個)</h3>
                <div class="price-stats">
                    <span>最低價格: <strong>$${priceStats.min.toLocaleString()}</strong></span>
                    <span>平均價格: <strong>$${priceStats.avg.toLocaleString()}</strong></span>
                    <span>最高價格: <strong>$${priceStats.max.toLocaleString()}</strong></span>
                </div>
                <div class="filter-options">
                    <select id="platformFilter" onchange="filterResults()">
                        <option value="all">所有平台</option>
                        ${getUniquePlatforms(listings).map(platform => 
                            `<option value="${platform}">${platform}</option>`
                        ).join('')}
                    </select>
                    <select id="conditionFilter" onchange="filterResults()">
                        <option value="all">所有狀況</option>
                        <option value="全新">全新</option>
                        <option value="二手">二手</option>
                    </select>
                    <select id="sortBy" onchange="sortResults()">
                        <option value="price">價格排序</option>
                        <option value="platform">平台排序</option>
                        <option value="condition">狀況排序</option>
                    </select>
                </div>
            </div>
            <div class="results-grid" id="resultsGrid">
                ${resultsHtml}
            </div>
        `;
        
        // 儲存原始結果供過濾使用
        window.currentResults = listings;
    }
    
    function groupByPlatform(listings) {
        const grouped = {};
        listings.forEach(listing => {
            if (!grouped[listing.platform]) {
                grouped[listing.platform] = [];
            }
            grouped[listing.platform].push(listing);
        });
        return grouped;
    }
    
    function calculatePriceStats(listings) {
        const prices = listings.map(l => l.price);
        return {
            min: Math.min(...prices),
            max: Math.max(...prices),
            avg: Math.round(prices.reduce((a, b) => a + b, 0) / prices.length)
        };
    }
    
    function getUniquePlatforms(listings) {
        return [...new Set(listings.map(l => l.platform))];
    }
    
    function truncateTitle(title, maxLength) {
        return title.length > maxLength ? title.substring(0, maxLength) + '...' : title;
    }
    
    function showError(message) {
        results.innerHTML = `<div class="error-message">${message}</div>`;
    }
    
    // 全域函數供HTML調用
    window.filterResults = function() {
        const platformFilter = document.getElementById('platformFilter').value;
        const conditionFilter = document.getElementById('conditionFilter').value;
        
        let filteredResults = window.currentResults;
        
        if (platformFilter !== 'all') {
            filteredResults = filteredResults.filter(item => item.platform === platformFilter);
        }
        
        if (conditionFilter !== 'all') {
            filteredResults = filteredResults.filter(item => item.condition === conditionFilter);
        }
        
        updateResultsDisplay(filteredResults);
    };
    
    window.sortResults = function() {
        const sortBy = document.getElementById('sortBy').value;
        let sortedResults = [...window.currentResults];
        
        switch(sortBy) {
            case 'price':
                sortedResults.sort((a, b) => a.price - b.price);
                break;
            case 'platform':
                sortedResults.sort((a, b) => a.platform.localeCompare(b.platform));
                break;
            case 'condition':
                sortedResults.sort((a, b) => a.condition.localeCompare(b.condition));
                break;
        }
        
        updateResultsDisplay(sortedResults);
    };
    
    window.toggleCompare = function(index) {
        // 實現商品比較功能
        console.log('Toggle compare for item:', index);
    };
    
    function updateResultsDisplay(listings) {
        const resultsGrid = document.getElementById('resultsGrid');
        
        const resultsHtml = listings.map((listing, index) => `
            <div class="result-card" data-index="${index}">
                <div class="result-header">
                    <div class="result-title" title="${listing.title}">${truncateTitle(listing.title, 60)}</div>
                    <div class="result-price">${listing.price.toLocaleString()}</div>
                </div>
                <div class="result-meta">
                    <span class="platform-badge platform-${listing.platform.toLowerCase().replace(/[^a-z0-9]/g, '')}">${listing.platform}</span>
                    <span class="condition-badge condition-${listing.condition}">${listing.condition}</span>
                    <span class="location">📍 ${listing.location}</span>
                </div>
                <div class="result-footer">
                    <span class="result-source">${listing.source}</span>
                    <div class="result-actions">
                        ${listing.url ? `<a href="${listing.url}" target="_blank" rel="noopener noreferrer" class="view-link">查看商品 ↗</a>` : ''}
                        <button class="compare-btn" onclick="toggleCompare(${index})">比較</button>
                    </div>
                </div>
            </div>
        `).join('');
        
        resultsGrid.innerHTML = resultsHtml;
    }
    
    async function loadSupportedPlatforms() {
        try {
            const response = await fetch('/api/platforms');
            const data = await response.json();
            console.log('支援的平台:', data.platforms);
        } catch (error) {
            console.error('載入平台清單失敗:', error);
        }
    }
});