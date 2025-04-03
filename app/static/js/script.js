// 선택된 카드 인덱스를 저장할 배열
let selectedCards = [];

// 카드 선택 토글 함수
function toggleCardSelection(card) {
    if (card.dataset.player !== 'Player 1') return;
    
    const index = parseInt(card.dataset.index);
    const selectedIndex = selectedCards.indexOf(index);
    
    if (selectedIndex === -1) {
        selectedCards.push(index);
        card.classList.add('selected');
    } else {
        selectedCards.splice(selectedIndex, 1);
        card.classList.remove('selected');
    }
}

// 카드 버리기 제출 함수
function submitDiscard() {
    document.getElementById('discardInput').value = selectedCards.join(',');
    document.getElementById('discardForm').submit();
}

// 카드 클릭 이벤트 리스너 등록
document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.card.selectable');
    cards.forEach(card => {
        card.addEventListener('click', function() {
            toggleCardSelection(this);
        });
    });

    // 초기 족보 하이라이트 적용
    highlightHandCards();
});

// 족보 하이라이트 관련 함수
function highlightHandCards() {
    // 이전 하이라이트 제거
    document.querySelectorAll('.card.hand-highlight').forEach(card => {
        card.classList.remove('hand-highlight');
    });

    // 각 플레이어의 족보 정보 가져오기
    document.querySelectorAll('.player-section').forEach(playerSection => {
        const handType = playerSection.querySelector('.score-info p:first-child')?.textContent;
        if (!handType) return;

        const cards = Array.from(playerSection.querySelectorAll('.card'));
        highlightCardsForHand(cards, handType);
    });
}

function highlightCardsForHand(cards, handInfo) {
    // 족보 정보에서 족보 타입 추출
    const handType = handInfo.split(': ')[1];
    if (!handType) return;

    const ranks = cards.map(card => {
        const rankMatch = card.textContent.match(/\d+|[JQKA]/);
        return rankMatch ? rankMatch[0] : '';
    });

    const suits = cards.map(card => {
        const suitClass = Array.from(card.querySelector('.small-suit').classList)
            .find(cls => ['hearts', 'diamonds', 'spades', 'clubs'].includes(cls));
        return suitClass;
    });

    // 족보별 하이라이트할 카드 찾기
    let cardsToHighlight = [];

    switch(handType) {
        case 'Royal Flush':
        case 'Straight Flush':
            const flushSuit = suits.find(suit => 
                suits.filter(s => s === suit).length >= 5
            );
            if (flushSuit) {
                cardsToHighlight = cards.filter((_, i) => suits[i] === flushSuit);
            }
            break;

        case 'Four of a Kind':
            const fourRank = ranks.find(rank => 
                ranks.filter(r => r === rank).length === 4
            );
            if (fourRank) {
                cardsToHighlight = cards.filter((_, i) => ranks[i] === fourRank);
            }
            break;

        case 'Full House':
            const threeRank = ranks.find(rank => 
                ranks.filter(r => r === rank).length === 3
            );
            const pairRank = ranks.find(rank => 
                rank !== threeRank && ranks.filter(r => r === rank).length >= 2
            );
            if (threeRank && pairRank) {
                cardsToHighlight = cards.filter((_, i) => 
                    ranks[i] === threeRank || ranks[i] === pairRank
                );
            }
            break;

        case 'Flush':
            const flushSuitType = suits.find(suit => 
                suits.filter(s => s === suit).length >= 5
            );
            if (flushSuitType) {
                cardsToHighlight = cards.filter((_, i) => suits[i] === flushSuitType);
            }
            break;

        case 'Straight':
            // 스트레이트의 경우 연속된 숫자 찾기
            const sortedRanks = ranks.map(r => {
                if (r === 'A') return 14;
                if (r === 'K') return 13;
                if (r === 'Q') return 12;
                if (r === 'J') return 11;
                return parseInt(r);
            }).sort((a, b) => a - b);

            for (let i = 0; i <= sortedRanks.length - 5; i++) {
                if (sortedRanks[i+4] - sortedRanks[i] === 4) {
                    const straightValues = new Set([
                        sortedRanks[i], sortedRanks[i+1], sortedRanks[i+2],
                        sortedRanks[i+3], sortedRanks[i+4]
                    ]);
                    cardsToHighlight = cards.filter((_, idx) => {
                        const cardValue = ranks[idx] === 'A' ? 14 :
                                        ranks[idx] === 'K' ? 13 :
                                        ranks[idx] === 'Q' ? 12 :
                                        ranks[idx] === 'J' ? 11 :
                                        parseInt(ranks[idx]);
                        return straightValues.has(cardValue);
                    });
                    break;
                }
            }
            break;

        case 'Three of a Kind':
            const tripleRank = ranks.find(rank => 
                ranks.filter(r => r === rank).length === 3
            );
            if (tripleRank) {
                cardsToHighlight = cards.filter((_, i) => ranks[i] === tripleRank);
            }
            break;

        case 'Two Pair':
            const pairs = ranks.filter((rank, i) => 
                ranks.indexOf(rank) === i && ranks.filter(r => r === rank).length === 2
            );
            if (pairs.length >= 2) {
                cardsToHighlight = cards.filter((_, i) => pairs.includes(ranks[i]));
            }
            break;

        case 'Pair':
            const pairRankOnly = ranks.find(rank => 
                ranks.filter(r => r === rank).length === 2
            );
            if (pairRankOnly) {
                cardsToHighlight = cards.filter((_, i) => ranks[i] === pairRankOnly);
            }
            break;
    }

    // 찾은 카드들에 하이라이트 효과 적용
    cardsToHighlight.forEach(card => {
        card.classList.add('hand-highlight');
    });
}

// 족보표 팝업 관련 함수
function showHandRankings() {
    document.getElementById('handRankingsPopup').style.display = 'block';
}

function hideHandRankings() {
    document.getElementById('handRankingsPopup').style.display = 'none';
}

// ESC 키로 팝업 닫기
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        hideHandRankings();
    }
});

// 팝업 외부 클릭시 닫기
document.addEventListener('click', function(event) {
    const popup = document.getElementById('handRankingsPopup');
    const popupContent = document.querySelector('.popup-content');
    if (event.target === popup) {
        hideHandRankings();
    }
});

// 페이지 로드 및 상태 변경시 하이라이트 갱신
document.addEventListener('DOMContentLoaded', highlightHandCards);
document.addEventListener('turbolinks:load', highlightHandCards);  // Turbolinks 사용시
window.addEventListener('load', highlightHandCards); 