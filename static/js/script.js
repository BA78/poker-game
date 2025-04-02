// 카드 선택 관리
let selectedCards = new Set();

function toggleCardSelection(card) {
    const index = card.dataset.index;
    if (selectedCards.has(index)) {
        selectedCards.delete(index);
        card.classList.remove('selected');
    } else {
        selectedCards.add(index);
        card.classList.add('selected');
    }
}

function submitDiscard() {
    const discardInput = document.getElementById('discardInput');
    discardInput.value = Array.from(selectedCards).join(',');
    document.getElementById('discardForm').submit();
}

// 페이지 로드 시 초기화 및 이벤트 리스너 설정
document.addEventListener('DOMContentLoaded', function() {
    selectedCards.clear();
    
    // 모든 카드에 대해 이벤트 리스너 추가
    document.querySelectorAll('.card').forEach(card => {
        if (card.dataset.player === 'Player 1') {
            card.addEventListener('click', function() {
                toggleCardSelection(this);
            });
        }
    });
}); 