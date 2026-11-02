'use strict';

const featTitle = `Why Choose Graphic Design Assist?`;

const feat1Title = `Professional Visual Branding`;
const feat1Desc = `
  At Graphic Design Solutions, we understand the unique challenges small businesses face in today's digital landscape. Visibility competitions are constantly evolving, and having a robust framework of user experience is essential to protect your business critical factors and maintain the trust of your customers.<br/> That's why we are committed to helping small businesses like yours.
`;

const feat2Title = `Consultation for UX Portfolio`;
const feat2Desc = `We offer expert consultations on graphic design and illustration, specifically tailored for small businesses and personal illustration products. Our free consultation service is designed to provide you with accessible, practical, and effective strategies to enhance your business awareness via graphic deliverables. Also, we have a program how to build personal graphic design portfolio. Our experienced professionals are here to guide you.`;
// const feat2Desc = `
//     Novice website creators often overlook critical features such as <a target='_blank' href='https://developer.mozilla.org/en-US/docs/Glossary/Semantics'>semantic design</a>, <a target='_blank' href='https://www.w3schools.com/html/html_responsive.asp'>mobile responsiveness</a>, <a target='_blank' href='https://www.ada.gov/resources/web-guidance/'>accessibility</a>, and <a target='_blank' href='https://developers.google.com/search/docs#what-is-seo '>SEO optimization</a>.<br/><br/>                    
//     Our Starter Kit ensures your website meets the modern web standards while enhancing your business credibility. With a custom domain name and a polished appearance, our kit simplifies professional website development.
// `;

const feat3Title = `Various Plans for buisness`;
const feat3Desc = `
    Yes! We have <span class='tile-text-bold'>"Free Consultation"</span><br/><br/>
    <span class='tile-text-bold'>"Reasonable Maintenance Cost"</span><br/><br/>
    We guide you through our custom <span class='tile-text-bold'>Consultation-plan</span> and  <span class='tile-text-bold'>reliable</span> Examples. Once we confirm which plan is optimal solution for your busines, .<br/><br/>
    The only optional ongoing expense is the annual domain registration (around $12 per year).
`;

const fillStaticText = () => {
  const phrase1Arr = phrase1.split(' ');
  getEl('js-title').innerHTML = phrase1;
  getEl('js-main-title').innerHTML = `${phrase1Arr[0]}<br/>${phrase1Arr[1]} ${phrase1Arr[2]}`;
  getEl('js-main-title').innerHTML = `Graphic Design Solutions`;
  // getEl('js-main-desc').innerHTML = mainDesc;
  getEl('js-feat1-title').innerHTML = `${feat1Title}<br/>`;
  getEl('js-feat2-title').innerHTML = `${feat2Title}<br/>`;
  // getEl('js-feat3-title').innerHTML = `${feat3Title}<br/>`;
  getEl('js-notice-success').innerHTML = messageSuccess;
  getEl('js-notice-err').innerHTML = messageFail;
  getEl('js-feat-title').innerHTML = featTitle;
  getEl('js-feat1-desc').innerHTML = feat1Desc;
  getEl('js-feat2-desc').innerHTML = feat2Desc;
  // getEl('js-feat3-desc').innerHTML = feat3Desc;
  
  getEl('js-contact-desc').innerHTML = `Getting started with decent illustrator design is easy. Simply sign up for our free consultation, and one of our experts will get in touch with you to discuss your specific needs and challenges. Together, we'll develop a comprehensive plan to enhance your graphic portfolio and ensure your portfolio perfection for your business.`;
   // or ${phone}`;

  getEl('js-contact-desc2').innerHTML = `<br/>If you have any questions, please feel free to contact us directly at <a href='mailto:${email}'>${email}</a>`;

  // getEl('js-contact-form').innerHTML = `<div class="contact-form-row">
  //   <div class="contact-form-text">
  //     <input type='off' class='form-textbox-input' id='name' name='name' autocomplete='nope' placeholder='Your name' required aria-label='Enter name'>
  //   </div>
  //   <div class='contact-form-sp'></div>
  //   <div class="contact-form-text">
  //     <input type='email' class='form-textbox-input' id='email' name='email' autocomplete='off' placeholder='Email address' required aria-label='Enter email'>
  //   </div>
  //   <div class='contact-form-sp'></div>
  //   <div id='js-contact-select' class="contact-form-text form-dropdown dropdown-fader">
  //     <select class="form-textbox-input form-dropdown-select" data-ignore-tracking="true" id="js-form-service" aria-labelledby="services-dropdown_label">
  //       <option disabled selected="" value="">Select a service type</option>
  //       <option class="services-dropdown-item" value="Starter Kit">Free Consulting</option>
  //       <option class="services-dropdown-item" value="Consulting">Tech Supports</option>
  //       <option class="services-dropdown-item" value="Others">Others</option>
  //     </select>
  //   </div>
  // </div>
  // <textarea placeholder="Please briefly explain your business and graphic needs." class="form-textbox-input contact-form-textarea" name="message" rows="10" required></textarea>
  // <button type='submit' class='button-blue'>Send your request</button>
  // `;
  getEl('js-footer').innerHTML = `© 2024 ${phrase1}`;
}

const renderBanner = async () => {
  await initBanner(0);

  const phraseArr = phrase1.split(' ');
  moveCaret('js-type-01');
  await elapseTime(500);
  getEl('js-header').scrollIntoView();
  await elapseTime(1500);
  await typeText('js-type-01', phraseArr[0], 70);
  await elapseTime(300);
  getEl('js-space-01').classList.remove('hidden');
  // getEl('js-next-01').classList.remove('hidden');
  if (isMobile())getEl('js-next-01').classList.remove('hidden'); 
  await typeText('js-type-02', phraseArr[1], 100);
  getEl('js-space-02').classList.remove('hidden');
  // if (isMobile())getEl('js-next-02').classList.remove('hidden'); 
  getEl('js-next-02').classList.remove('hidden');
  await typeText('js-type-03', phraseArr[2], 40);
  blinkCaret(true);
  getEl('js-main-img-1').classList.add('bw-opacity-trans');
  await elapseTime(2000);

  // await selectText('js-type-01', 50);
  // await elapseTime(1000);
  // getEl('js-type-01').innerHTML = '';
  // moveCaret('js-type-01');
  // blinkCaret(false);
  // await elapseTime(100);
  // getEl('js-type-01').classList.add('text-subhead');
  // await typeText('js-type-01', phrase2.split(' ')[0], 30);

  // await selectText('js-type-03', 50);
  // await elapseTime(1000);
  // getEl('js-type-03').innerHTML = '';
  // moveCaret('js-type-03');
  // blinkCaret(false);
  // await elapseTime(100);
  // getEl('js-type-03').classList.add('text-subhead');
  // await typeText('js-type-03', phrase2.split(' ')[2], 30);
  // blinkCaret(true);
  // await elapseTime(1500);
   
  await initBanner(0);
  
  if (!isMobile()) getEl('js-banner-wr').style.lineHeight = 2;
  
  const phrase3Arr = phrase3.split(' ');
  moveCaret('js-type-01');
  await typeText('js-type-01', phrase3Arr[0], 50);
  getEl('js-space-01').classList.remove('hidden');
  await typeText('js-type-02', phrase3Arr[1], 100);
  getEl('js-space-02').classList.remove('hidden');
  if (isMobile())getEl('js-next-02').classList.remove('hidden'); 
  await typeText('js-type-03', phrase3Arr[2], 20);
  await elapseTime(1000);

  await selectText('js-type-03', 50);
  await elapseTime(1000);
  getEl('js-type-03').innerHTML = '';
  moveCaret('js-type-03');
  blinkCaret(false);


  hideCaret();
  getEl('js-type-03').style.color = '#a2a2a2';
  getEl('js-type-03').innerHTML = phrase4.split(' ')[2];
  moveSwitch('js-next-02');
  await expandSwitch(3);
  await elapseTime(500);
  await turnOnSwitch(20);
  getEl('js-type-03').classList.add('font-color-transition');
  getEl('js-main-img-2').classList.add('col-opacity-trans');
  blinkCaret();

  await elapseTime(1500);
  getEl('js-switch-wr').remove();
  await initBanner(180);
  const phrase5Arr = phrase5.split(' ');
  
  moveCaret('js-type-01');
  await elapseTime(1500);
  await typeText('js-type-01', phrase5Arr[0], 50);
  getEl('js-space-01').classList.remove('hidden');
  // await typeText('js-type-02', phrase5Arr[1], 100);
  getEl('js-space-02').classList.remove('hidden');
  if (isMobile())getEl('js-next-02').classList.remove('hidden'); 
  // await typeText('js-type-03', phrase5Arr[2], 20);
  await elapseTime(500);

  // await elapseTime(2000);
  getEl('js-type-03').innerHTML = '';
  moveCaret('js-type-03');

  hideCaret();
  getEl('js-type-03').classList.remove('font-color-transition');
  getEl('js-type-03').innerHTML = phrase5.split(' ')[1];
  getEl('js-type-03').style.color = '#fff';
  moveVolume('js-next-02');
  await startVolume('js-type-03', 500);
  blinkCaret();
  await elapseTime(1200);

  getEl('js-main-img-3').classList.add('full-opacity-trans'); // color img
  getEl('js-volume-wr').remove(); // remove speaker
  getEl('js-type-03').classList.remove('vol-color-high', 'vol-color-low', 'vol-color-off');
  await initBanner(30);

  // getEl('js-main-img-3').classList.add('full-opacity-trans');
  await elapseTime(1500);

  getEl('js-banner-wr').style.textAlign = 'center'; // list one is centered
  if (isMobile()) {
    getEl('js-banner-wr').style.marginLeft = 0;
    getEl('js-banner-wr').style.lineHeight = 0.4;
    getEl('js-type-02').style.lineHeight = 2.1;
  }

  const phrase6Arr = phrase6.split(' ');

  if (isMobile()) getEl('js-banner-wr').style.paddingLeft = 0;
  getEl('js-type-01').style.color = '#fff';
  getEl('js-type-02').style.color = '#fff';
  getEl('js-type-03').style.color = '#fff';
  moveCaret('js-type-01');
  await typeText('js-type-01', phrase6Arr[0], 50);
  getEl('js-space-01').classList.remove('hidden');
  if (isMobile())getEl('js-next-01').classList.remove('hidden'); 
  // await typeText('js-type-02', phrase6Arr[1], 100);
  getEl('js-space-02').classList.remove('hidden');
  if (isMobile())getEl('js-next-02').classList.remove('hidden'); 
  await typeText('js-type-03', phrase6Arr[1], 40);
  await elapseTime(1500);
  getEl('js-main-img-1').style.opacity = 0;  // bw 이미지 완전 숨김
  getEl('js-main-img-2').style.opacity = 0;  // partial 컬러 완전 숨김
  getEl('js-main-img-3').style.opacity = 1;  // full은 유지

  hideCaret();
  getEl('js-type-02').innerHTML = `<div class='image-wr globe-wr fi-short'><img  id='js-globe' class='globe-size' src='./icon/globe-white-solid.svg'></div>`;
  await elapseTime(1000);

  getEl('js-link').style.opacity = 1;
  getEl('js-link-details').classList.add('flashing');

}

const gotoHome = () => {
  window.location.href = './index.html';
}

const startEventListener = () => {
  startContactListener(); // start listener
}

const main = async () => {
  await loadEnv();
  startEventListener();

  // if (!isMobile()) {
  //   getEl('js-main-img-1').src = './img/banner-bw.jpg';
  //   getEl('js-main-img-2').src = './img/banner-col.jpg';
  //   getEl('js-main-img-3').src = './img/banner-full.jpg';
  // }
  if (!isMobile()) {
    getEl('js-main-img-1').src = './img/rainier-sea.jpg';  //  바다와 산 (bw 효과로 사용, CSS에서 grayscale 적용)
    getEl('js-main-img-2').src = './img/seattle-rainier-event.jpg';  // 도시와 산, Space Needle 포함
    getEl('js-main-img-3').src = './img/rainier-sunset-chess.jpg';  //  체스판과 산 sunset
  } else {
    getEl('js-main-img-1').src = './img/rainier-sea-m.jpg';  // 모바일 버전 (원본처럼 -m 접미사 가정, 필요 시 리사이즈)
    getEl('js-main-img-2').src = './img/seattle-rainier-event-m.jpg';
    getEl('js-main-img-3').src = './img/rainier-sunset-chess-m.jpg';
  }
  await loadFont();

  renderBanner();
  fillStaticText();


}

main();