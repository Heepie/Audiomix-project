$(document).ready(function() {
    // waveform 클래스를 가진 div 목록 가져옴
    var div_list = document.getElementsByClassName('waveform');
    // 목록을 순회하면서
    for (var i = 0; i < div_list.length; i++) {
        // div의 datasrc 속성의 값을 track_url 변수에 저장
        var track_url = div_list[i].getAttribute('datasrc');
        // waveform을 그려줄 각각의 div에 부여할 id값 생성
        var waveform_id = '#waveform-' + (i + 1);
        // track_url와 waveform_id를 drawTrack 함수에 전달
        drawTrack(track_url, waveform_id)
    }

    // 파일 위치 url과 waveform을 그려줄 div를 지정하는 element_id 인자를 받음
    function drawTrack(url, element_id) {
        // waveform 객체 생성
        var wavesurfer = WaveSurfer.create({
            // 대상 객체 id값(필수)
            container: element_id,
            // 막대 넓이
            barWidth: 4,
            // 막대 높이
            barHeight: 0.8,
            // 커서 이전 부분 색상
            progressColor: '#E2B026',
            // 커서 색상
            cursorColor: 'transparent',
            // 커서 이후 부분 색상
            waveColor: '#333533'
        });
        // waveform 객체 로드
        wavesurfer.load(url);
        // waveform 로딩이 끝나면 함수 실행
        wavesurfer.on("ready", function() {
            // loader를 없애주는 함수
            waveformLoader();
        });
    }
});

// loader를 없애주는 함수
function waveformLoader() {
    // waveform-loader라는 클래스명을 가진 객체 리스트 저장
    var loader = document.getElementsByClassName('waveform-loader');

    // 리스트를 순회하면서 display 속성을 none으로 변경
    for (var i = 0; i < loader.length; i++) {
        loader[i].style.display = 'none';
    }
}
