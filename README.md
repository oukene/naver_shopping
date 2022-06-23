네이버 API 를 이용하여 쇼핑 검색을 하는 통합구성요소입니다.

[설치 방법]

- 네이버 API 발급

https://developers.naver.com/apps/#/register
네이버 개발자 센터에서 애플리케이션 등록후 키 발급

Client ID 와 Client Secret 키를 설치시에 입력


수동설치

소스코드를 다운로드 받은 후 HA 내부의 custom_components 경로에 naver_shopping 폴더를 넣어주고 재시작
HACS

HACS 의 custom repository에 https://github.com/oukene/naver_shopping 주소를 integration 으로 추가 후 설치
설치 후 통합구성요소 추가하기에서 naver_shopping 검색 하여 설치한 후 구성 옵션 변경을 통해서 추가 가능합니다.

검색어를 추가 한 후 다시 읽어오기를 하면 검색결과의 최저가가 센서의 값으로 설정됩니다.



History
v1.0.0 - 2022.02.10 - 최초 작성
