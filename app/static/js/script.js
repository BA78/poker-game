// 선택된 카드 인덱스를 저장할 배열
let selectedCards = [];

const MAX_CARDS_TO_DISCARD = 5;

// 카드 선택 토글 함수
function toggleCardSelection(card) {
    if (card.dataset.player !== 'Player 1') return;
    
    const index = parseInt(card.dataset.index);
    const selectedIndex = selectedCards.indexOf(index);
    
    if (selectedIndex === -1) {
        // 이미 최대 카드를 선택했는지 확인
        if (selectedCards.length >= MAX_CARDS_TO_DISCARD) {
            alert(`최대 ${MAX_CARDS_TO_DISCARD}장의 카드만 교체할 수 있습니다.`);
            return;
        }
        
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
    
    // 선택된 카드 수에 따라 UI 업데이트
    updateCardSelectionUI();
}

// 카드 선택 UI 업데이트 함수
function updateCardSelectionUI() {
    const cardsSelectedText = document.getElementById('cardsSelectedText');
    if (cardsSelectedText) {
        cardsSelectedText.textContent = `선택된 카드: ${selectedCards.length}/${MAX_CARDS_TO_DISCARD}`;
    }
    
    // 버튼 텍스트 업데이트
    const discardButton = document.getElementById('discardButton');
    if (discardButton) {
        discardButton.textContent = `선택한 카드 교체 (${selectedCards.length}/${MAX_CARDS_TO_DISCARD})`;
        discardButton.disabled = selectedCards.length === 0;
    }
}

// 카드 버리기 제출 함수
function submitDiscard() {
    console.log("[디버깅] submitDiscard 함수 호출됨");
    const selectedEls = document.querySelectorAll('.card.selectable.selected');
    
    // 선택된 카드가 없는 경우 알림 표시
    if (selectedEls.length === 0) {
        alert("교체할 카드를 선택하거나, 카드를 유지하려면 '턴 넘기기' 버튼을 클릭하세요.");
        return;
    }
    
    // 선택된 카드의 데이터 출력 (디버깅)
    console.log("[디버깅] 선택된 카드 요소:", selectedEls);
    
    const indices = Array.from(selectedEls).map(card => card.dataset.index);
    console.log("[디버깅] 선택된 카드 인덱스:", indices);
    console.log("[디버깅] 전송될 데이터:", indices.join(','));

    document.getElementById('discardInput').value = indices.join(',');
    
    // 폼 유효성 검사
    const form = document.getElementById('discardForm');
    if (validateFormBeforeSubmit(form)) {
        console.log("[디버깅] 폼 제출됨");
        form.submit();
    }
}

function validateFormBeforeSubmit(form) {
    // CSRF 토큰 확인
    const csrfToken = form.querySelector('input[name="csrf_token"]');
    if (!csrfToken || !csrfToken.value) {
        console.error("CSRF 토큰이 없습니다!");
        location.reload();
        return false;
    }
    
    return true;
}

// 카드 클릭 이벤트 리스너 등록
document.addEventListener('click', function (e) {
    const card = e.target.closest('.card.selectable');
    if (card) {
        toggleCardSelection(card);
    }
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

// 개선된 카드 값 매핑 함수
function getCardNumericValue(rank) {
    if (rank === 'A' || rank === 'Ace') return 14;
    if (rank === 'K' || rank === 'King') return 13;
    if (rank === 'Q' || rank === 'Queen') return 12;
    if (rank === 'J' || rank === 'Jack') return 11;
    return parseInt(rank) || 0;
}

function highlightCardsForHand(cards, handInfo) {
    // 족보 정보에서 족보 타입 추출
    const handType = handInfo.split(': ')[1];
    if (!handType) return;

    // 디버깅 로그 추가
    console.log("하이라이트 함수 호출됨 - 족보 타입:", handType);
    
    // 랭크 및 무늬 추출 방식 개선
    const ranks = cards.map(card => {
        // dataset에서 값을 가져오거나, 텍스트 콘텐츠에서 추출
        if (card.dataset.rank) return card.dataset.rank;
        
        // 텍스트 콘텐츠에서 추출하는 대안 방법
        const centerText = card.querySelector('.big-text, .big-number, .rank-top');
        return centerText ? centerText.textContent.trim() : '';
    });
    
    const suits = cards.map(card => {
        // dataset에서 값을 가져오거나, 클래스에서 추출
        if (card.dataset.suit) return card.dataset.suit;
        
        // 클래스에서 추출하는 대안 방법
        const suitElement = card.querySelector('.small-suit');
        if (suitElement) {
            const suitClass = Array.from(suitElement.classList).find(cls => 
                ['hearts', 'diamonds', 'spades', 'clubs'].includes(cls));
            return suitClass ? suitClass.charAt(0).toUpperCase() + suitClass.slice(1) : '';
        }
        return '';
    });
    
    // 디버깅 로그
    console.log("카드 랭크:", ranks);
    console.log("카드 무늬:", suits);
    
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
            // 스트레이트 개선된 로직
            const numericRanks = ranks.map(r => getCardNumericValue(r));
            
            // 디버깅: 숫자화된 랭크 출력
            console.log("숫자화된 랭크:", numericRanks);
            
            // 중복 제거 및 정렬
            const uniqueRanks = [...new Set(numericRanks)].sort((a, b) => a - b);
            
            // A-5 스트레이트 체크 (A를 1로 취급)
            const hasAce = uniqueRanks.includes(14);
            if (hasAce && uniqueRanks.includes(2) && 
                uniqueRanks.includes(3) && uniqueRanks.includes(4) && 
                uniqueRanks.includes(5)) {
                const lowStraightValues = new Set([14, 2, 3, 4, 5]);
                cardsToHighlight = cards.filter((_, idx) => {
                    const cardValue = numericRanks[idx];
                    return lowStraightValues.has(cardValue);
                });
                break;
            }
            
            // 연속된 5개 이상의 카드 찾기 (개선된 알고리즘)
            let maxLength = 0;
            let straightSeq = [];
            let currentSeq = [uniqueRanks[0]];
            
            for (let i = 1; i < uniqueRanks.length; i++) {
                if (uniqueRanks[i] === uniqueRanks[i-1] + 1) {
                    // 연속된 숫자
                    currentSeq.push(uniqueRanks[i]);
                } else {
                    // 연속이 끊어짐
                    if (currentSeq.length >= 5 && currentSeq.length > maxLength) {
                        maxLength = currentSeq.length;
                        straightSeq = [...currentSeq];
                    }
                    currentSeq = [uniqueRanks[i]];
                }
            }
            
            // 마지막 시퀀스 확인
            if (currentSeq.length >= 5 && currentSeq.length > maxLength) {
                straightSeq = [...currentSeq];
            }
            
            // 스트레이트가 있으면 해당 카드 하이라이트
            if (straightSeq.length >= 5) {
                const straightValues = new Set(straightSeq);
                cardsToHighlight = cards.filter((_, idx) => {
                    const cardValue = numericRanks[idx];
                    return straightValues.has(cardValue);
                });
            } else {
                // 연결된 카드가 정확히 5장은 아니지만 5장 이상인 경우의 스트레이트 찾기
                for (let i = 0; i <= uniqueRanks.length - 5; i++) {
                    const consecutive = uniqueRanks.slice(i, i + 5);
                    if (consecutive[4] - consecutive[0] === 4) {
                        const straightValues = new Set(consecutive);
                        cardsToHighlight = cards.filter((_, idx) => {
                            const cardValue = numericRanks[idx];
                            return straightValues.has(cardValue);
                        });
                        break;
                    }
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

    // 더 많은 디버깅 정보 추가
    console.log("하이라이트 대상 카드:", cardsToHighlight.length);
    cardsToHighlight.forEach(card => {
        console.log("하이라이트 카드:", card.dataset.rank, card.dataset.suit);
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

document.addEventListener('DOMContentLoaded', function() {
    // 게임 상태 확인
    const winnerElement = document.querySelector('.winner');
    
    if (winnerElement) {
        // 게임이 종료된 경우 모든 게임 관련 버튼 비활성화
        const gameButtons = document.querySelectorAll('.game-controls .btn:not([href*="play_computer"])');
        gameButtons.forEach(button => {
            button.classList.add('disabled');
            
            // <a> 태그인 경우
            if (button.tagName === 'A') {
                button.addEventListener('click', function(e) {
                    e.preventDefault();
                    console.log('게임이 이미 종료되었습니다.');
                });
            } else {
                // 버튼인 경우
                button.disabled = true;
            }
        });
    }
});

// AJAX POST 요청 예시
function ajaxPost(url, data) {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('Error:', error));
} 