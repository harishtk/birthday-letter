const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

function page(now) {
  const elements = new Map();
  function element(key) {
    if (!elements.has(key)) elements.set(key, {textContent: '', hidden: true, dataset: {}, classList: {remove(){}, add(){}}, addEventListener(){}});
    return elements.get(key);
  }
  element('birthday-data').dataset.config = JSON.stringify({target:'2026-12-05T00:00:00+05:30',serverNow:now,name:'Darling',fortunes:['Lovely things ahead']});
  const context = {document:{getElementById:element,querySelector:element,querySelectorAll:()=>[],addEventListener(){},title:''},window:{matchMedia:()=>({matches:true}),addEventListener(){}},Date,setInterval(){},fetch(){throw Error('offline')},console};
  vm.createContext(context);
  vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);
  return {context,element};
}
test('India midnight is Dec 4 18:30 UTC, with one second left just before',()=>{
  const {context,element}=page('2026-12-04T18:29:59Z');
  assert.equal(element('seconds').textContent,'01');
  assert.equal(element('celebrate').hidden,true);
  vm.runInContext('offset += 1000; tick()',context);
  assert.equal(element('seconds').textContent,'00');
  assert.equal(element('hero-title').textContent,'Happy birthday, Darling!');
  assert.equal(element('celebrate').hidden,false);
});
test('opening after birthday shows celebration without negative values',()=>{
  const {element}=page('2026-12-06T18:30:00Z');
  for(const unit of ['days','hours','minutes','seconds']) assert.equal(element(unit).textContent,'00');
  assert.equal(element('hero-title').textContent,'Happy birthday, Darling!');
});
