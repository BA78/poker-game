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
        // 선택 시 반짝임 효과 제거
        if (card.classList.contains('hand-highlight')) {
            card.classList.remove('hand-highlight');
            card.classList.add('was-highlighted');
        }
    } else {
        selectedCards.splice(selectedIndex, 1);
        card.classList.remove('selected');
        // 선택 해제 시 이전에 반짝이던 카드였다면 다시 반짝임 효과 추가
        if (card.classList.contains('was-highlighted')) {
            card.classList.remove('was-highlighted');
            card.classList.add('hand-highlight');
        }
    }
}

// 카드 버리기 제출 함수
function submitDiscard() {
    document.getElementById('discardInput').value = selectedCards.join(',');
    document.getElementById('discardForm').submit();
    
    // 카드를 버린 후 하이라이트 갱신을 여러 번 시도
    setTimeout(highlightHandCards, 500);  // 첫 번째 시도
    setTimeout(highlightHandCards, 1000); // 두 번째 시도
    setTimeout(highlightHandCards, 1500); // 세 번째 시도
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
    setTimeout(highlightHandCards, 100);  // 약간의 지연 후 첫 적용
    setTimeout(highlightHandCards, 500);  // 한번 더 시도
});

// 페이지 로드 및 상태 변경시 하이라이트 갱신
document.addEventListener('DOMContentLoaded', () => {
    // 초기 하이라이트 적용
    setTimeout(highlightHandCards, 100);
    setTimeout(highlightHandCards, 500);
    
    // DOM 변경 감시 시작
    observeGameChanges();
});

// 게임 상태 변경 감지 및 하이라이트 갱신
function observeGameChanges() {
    // 점수 정보 변경 감시
    const scoreObserver = new MutationObserver(() => {
        setTimeout(highlightHandCards, 100);
    });

    // 카드 컨테이너 변경 감시 (카드 추가/제거/정렬)
    const cardContainerObserver = new MutationObserver(() => {
        setTimeout(highlightHandCards, 100);
    });

    // 전체 게임 영역 변경 감시 (게임 시작/종료)
    const gameAreaObserver = new MutationObserver(() => {
        setTimeout(highlightHandCards, 100);
        setTimeout(highlightHandCards, 500);
    });

    // 점수 정보 감시 설정
    document.querySelectorAll('.score-info').forEach(scoreInfo => {
        scoreObserver.observe(scoreInfo, {
            characterData: true,
            childList: true,
            subtree: true
        });
    });

    // 카드 컨테이너 감시 설정
    document.querySelectorAll('.cards-container').forEach(container => {
        cardContainerObserver.observe(container, {
            childList: true,
            subtree: true,
            attributes: true,
            characterData: true
        });
    });

    // 게임 영역 감시 설정
    const gameArea = document.querySelector('.game-area');
    if (gameArea) {
        gameAreaObserver.observe(gameArea, {
            childList: true,
            subtree: true
        });
    }

    // 게임 컨트롤 영역 감시 설정 (게임 시작/종료 버튼)
    const gameControls = document.querySelector('.game-controls');
    if (gameControls) {
        gameAreaObserver.observe(gameControls, {
            childList: true,
            subtree: true
        });
    }
}

// 족보 하이라이트 관련 함수
function highlightHandCards() {
    // 이전 하이라이트 제거
    document.querySelectorAll('.card.hand-highlight').forEach(card => {
        if (!card.classList.contains('selected')) {
            card.classList.remove('hand-highlight');
        }
    });

    // was-highlighted 클래스도 제거 (선택되지 않은 카드만)
    document.querySelectorAll('.card.was-highlighted').forEach(card => {
        if (!card.classList.contains('selected')) {
            card.classList.remove('was-highlighted');
        }
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

            // A-5 스트레이트 체크 (A를 1로 취급)
            const hasAce = sortedRanks.includes(14);
            if (hasAce) {
                const lowStraight = [2, 3, 4, 5];
                if (lowStraight.every(rank => sortedRanks.includes(rank))) {
                    const straightValues = new Set([14, ...lowStraight]);
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

            // 일반적인 스트레이트 체크
            for (let i = 0; i <= sortedRanks.length - 5; i++) {
                const consecutive = sortedRanks.slice(i, i + 5);
                if (consecutive[4] - consecutive[0] === 4) {
                    const straightValues = new Set(consecutive);
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