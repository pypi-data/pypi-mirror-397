/*! For license information please see 26321.5bd5ddd76b129071.js.LICENSE.txt */
(self.webpackChunkhome_assistant_frontend=self.webpackChunkhome_assistant_frontend||[]).push([["26321"],{69709:function(e,t,n){"use strict";var o=n(59787),r=(n(74423),n(23792),n(72712),n(18111),n(22489),n(61701),n(18237),n(3362),n(27495),n(62953),n(40445)),a=n(96196),i=n(77845),s=n(1420),l=n(30015),c=n.n(l),d=n(1087),h=(n(3296),n(27208),n(48408),n(14603),n(47566),n(98721),n(2209));let u;var p=n(996);let m,g=e=>e;const f=e=>(0,a.qy)(m||(m=g`${0}`),e),v=new p.G(1e3),b={reType:(0,o.A)(/((\[!(caution|important|note|tip|warning)\])(?:\s|\\n)?)/i,{input:1,type:3}),typeToHaAlert:{caution:"error",important:"info",note:"info",tip:"success",warning:"warning"}};class y extends a.mN{disconnectedCallback(){if(super.disconnectedCallback(),this.cache){const e=this._computeCacheKey();v.set(e,this.innerHTML)}}createRenderRoot(){return this}update(e){super.update(e),void 0!==this.content&&(this._renderPromise=this._render())}async getUpdateComplete(){return await super.getUpdateComplete(),await this._renderPromise,!0}willUpdate(e){if(!this.innerHTML&&this.cache){const e=this._computeCacheKey();v.has(e)&&((0,a.XX)(f((0,s._)(v.get(e))),this.renderRoot),this._resize())}}_computeCacheKey(){return c()({content:this.content,allowSvg:this.allowSvg,allowDataUrl:this.allowDataUrl,breaks:this.breaks})}async _render(){const e=await(async(e,t,o)=>(u||(u=(0,h.LV)(new Worker(new URL(n.p+n.u("55640"),n.b)))),u.renderMarkdown(e,t,o)))(String(this.content),{breaks:this.breaks,gfm:!0},{allowSvg:this.allowSvg,allowDataUrl:this.allowDataUrl});(0,a.XX)(f((0,s._)(e.join(""))),this.renderRoot),this._resize();const t=document.createTreeWalker(this,NodeFilter.SHOW_ELEMENT,null);for(;t.nextNode();){const e=t.currentNode;if(e instanceof HTMLAnchorElement&&e.host!==document.location.host)e.target="_blank",e.rel="noreferrer noopener";else if(e instanceof HTMLImageElement)this.lazyImages&&(e.loading="lazy"),e.addEventListener("load",this._resize);else if(e instanceof HTMLQuoteElement){var o;const n=(null===(o=e.firstElementChild)||void 0===o||null===(o=o.firstChild)||void 0===o?void 0:o.textContent)&&b.reType.exec(e.firstElementChild.firstChild.textContent);if(n){const{type:o}=n.groups,r=document.createElement("ha-alert");r.alertType=b.typeToHaAlert[o.toLowerCase()],r.append(...Array.from(e.childNodes).map(e=>{const t=Array.from(e.childNodes);if(!this.breaks&&t.length){var o;const e=t[0];e.nodeType===Node.TEXT_NODE&&e.textContent===n.input&&null!==(o=e.textContent)&&void 0!==o&&o.includes("\n")&&(e.textContent=e.textContent.split("\n").slice(1).join("\n"))}return t}).reduce((e,t)=>e.concat(t),[]).filter(e=>e.textContent&&e.textContent!==n.input)),t.parentNode().replaceChild(r,e)}}else e instanceof HTMLElement&&["ha-alert","ha-qr-code","ha-icon","ha-svg-icon"].includes(e.localName)&&n(96175)(`./${e.localName}`)}}constructor(...e){super(...e),this.allowSvg=!1,this.allowDataUrl=!1,this.breaks=!1,this.lazyImages=!1,this.cache=!1,this._renderPromise=Promise.resolve(),this._resize=()=>(0,d.r)(this,"content-resize")}}(0,r.__decorate)([(0,i.MZ)()],y.prototype,"content",void 0),(0,r.__decorate)([(0,i.MZ)({attribute:"allow-svg",type:Boolean})],y.prototype,"allowSvg",void 0),(0,r.__decorate)([(0,i.MZ)({attribute:"allow-data-url",type:Boolean})],y.prototype,"allowDataUrl",void 0),(0,r.__decorate)([(0,i.MZ)({type:Boolean})],y.prototype,"breaks",void 0),(0,r.__decorate)([(0,i.MZ)({type:Boolean,attribute:"lazy-images"})],y.prototype,"lazyImages",void 0),(0,r.__decorate)([(0,i.MZ)({type:Boolean})],y.prototype,"cache",void 0),y=(0,r.__decorate)([(0,i.EM)("ha-markdown-element")],y)},3587:function(e,t,n){"use strict";n(23792),n(3362),n(62953);var o=n(40445),r=n(96196),a=n(77845);n(69709);let i,s,l=e=>e;class c extends r.WF{async getUpdateComplete(){var e;const t=await super.getUpdateComplete();return await(null===(e=this._markdownElement)||void 0===e?void 0:e.updateComplete),t}render(){return this.content?(0,r.qy)(i||(i=l`<ha-markdown-element .content="${0}" .allowSvg="${0}" .allowDataUrl="${0}" .breaks="${0}" .lazyImages="${0}" .cache="${0}"></ha-markdown-element>`),this.content,this.allowSvg,this.allowDataUrl,this.breaks,this.lazyImages,this.cache):r.s6}constructor(...e){super(...e),this.allowSvg=!1,this.allowDataUrl=!1,this.breaks=!1,this.lazyImages=!1,this.cache=!1}}c.styles=(0,r.AH)(s||(s=l`
    :host {
      display: block;
    }
    ha-markdown-element {
      -ms-user-select: text;
      -webkit-user-select: text;
      -moz-user-select: text;
    }
    ha-markdown-element > *:first-child {
      margin-top: 0;
    }
    ha-markdown-element > *:last-child {
      margin-bottom: 0;
    }
    ha-alert {
      display: block;
      margin: var(--ha-space-1) 0;
    }
    a {
      color: var(--markdown-link-color, var(--primary-color));
    }
    img {
      background-color: var(--markdown-image-background-color);
      border-radius: var(--markdown-image-border-radius);
      max-width: 100%;
    }
    p:first-child > img:first-child {
      vertical-align: top;
    }
    p:first-child > img:last-child {
      vertical-align: top;
    }
    ha-markdown-element > :is(ol, ul) {
      padding-inline-start: var(--markdown-list-indent, revert);
    }
    li {
      &:has(input[type="checkbox"]) {
        list-style: none;
        & > input[type="checkbox"] {
          margin-left: 0;
        }
      }
    }
    svg {
      background-color: var(--markdown-svg-background-color, none);
      color: var(--markdown-svg-color, none);
    }
    code,
    pre {
      background-color: var(--markdown-code-background-color, none);
      border-radius: var(--ha-border-radius-sm);
      color: var(--markdown-code-text-color, inherit);
    }
    code {
      font-size: var(--ha-font-size-s);
      padding: 0.2em 0.4em;
    }
    pre code {
      padding: 0;
    }
    pre {
      padding: var(--ha-space-4);
      overflow: auto;
      line-height: var(--ha-line-height-condensed);
      font-family: var(--ha-font-family-code);
    }
    h1,
    h2,
    h3,
    h4,
    h5,
    h6 {
      line-height: initial;
    }
    h2 {
      font-size: var(--ha-font-size-xl);
      font-weight: var(--ha-font-weight-bold);
    }
    hr {
      border-color: var(--divider-color);
      border-bottom: none;
      margin: var(--ha-space-4) 0;
    }
    table[role="presentation"] {
      --markdown-table-border-collapse: separate;
      --markdown-table-border-width: attr(border, 0);
      --markdown-table-padding-inline: 0;
      --markdown-table-padding-block: 0;
      th {
        vertical-align: attr(align, center);
      }
      td {
        vertical-align: attr(align, left);
      }
    }
    table {
      border-collapse: var(--markdown-table-border-collapse, collapse);
    }
    div:has(> table) {
      overflow: auto;
    }
    th {
      text-align: var(--markdown-table-text-align, start);
    }
    td,
    th {
      border-width: var(--markdown-table-border-width, 1px);
      border-style: var(--markdown-table-border-style, solid);
      border-color: var(--markdown-table-border-color, var(--divider-color));
      padding-inline: var(--markdown-table-padding-inline, 0.5em);
      padding-block: var(--markdown-table-padding-block, 0.25em);
    }
    blockquote {
      border-left: 4px solid var(--divider-color);
      margin-inline: 0;
      padding-inline: 1em;
    }
  `)),(0,o.__decorate)([(0,a.MZ)()],c.prototype,"content",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:"allow-svg",type:Boolean})],c.prototype,"allowSvg",void 0),(0,o.__decorate)([(0,a.MZ)({attribute:"allow-data-url",type:Boolean})],c.prototype,"allowDataUrl",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean})],c.prototype,"breaks",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean,attribute:"lazy-images"})],c.prototype,"lazyImages",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean})],c.prototype,"cache",void 0),(0,o.__decorate)([(0,a.P)("ha-markdown-element")],c.prototype,"_markdownElement",void 0),c=(0,o.__decorate)([(0,a.EM)("ha-markdown")],c)},84334:function(e,t,n){"use strict";n.d(t,{H:function(){return r},R:function(){return o}});const o=(e,t,n)=>e.subscribeMessage(e=>t(e),Object.assign({type:"render_template"},n)),r=(e,t,n,o,r)=>e.connection.subscribeMessage(r,{type:"template/start_preview",flow_id:t,flow_type:n,user_input:o})},67334:function(e,t,n){"use strict";n.r(t),n.d(t,{HuiMarkdownCard:function(){return b}});n(49255),n(16280),n(23792),n(3362),n(62953);var o=n(40445),r=n(96196),a=n(77845),i=n(94333),s=n(30015),l=n.n(s),c=n(42372),d=n(1087),h=(n(38962),n(76776),n(3587),n(84334)),u=n(996);let p,m,g,f=e=>e;const v=new u.G(1e3);class b extends r.WF{static async getConfigElement(){return await n.e("90742").then(n.bind(n,4757)),document.createElement("hui-markdown-card-editor")}static getStubConfig(){return{type:"markdown",content:"The **Markdown** card allows you to write any text. You can style it **bold**, *italicized*, ~strikethrough~ etc. You can do images, links, and more.\n\nFor more information see the [Markdown Cheatsheet](https://commonmark.org/help)."}}getCardSize(){return void 0===this._config?3:void 0===this._config.card_size?Math.round(this._config.content.split("\n").length/2)+(this._config.title?1:0):this._config.card_size}setConfig(e){var t;if(!e.content)throw new Error("Content required");(null===(t=this._config)||void 0===t?void 0:t.content)!==e.content&&this._tryDisconnect(),this._config=e}connectedCallback(){super.connectedCallback(),this._tryConnect()}_computeCacheKey(){return l()(this._config)}disconnectedCallback(){if(super.disconnectedCallback(),this._tryDisconnect(),this._config&&this._templateResult){const e=this._computeCacheKey();v.set(e,this._templateResult)}}willUpdate(e){if(super.willUpdate(e),this._config&&!this._templateResult){const e=this._computeCacheKey();v.has(e)&&(this._templateResult=v.get(e))}}render(){var e,t,n;return this._config?(0,r.qy)(p||(p=f` ${0} <ha-card .header="${0}" class="${0}"> <ha-markdown cache breaks .content="${0}"></ha-markdown> </ha-card> `),this._error?(0,r.qy)(m||(m=f` <ha-alert .alertType="${0}"> ${0} </ha-alert> `),(null===(e=this._errorLevel)||void 0===e?void 0:e.toLowerCase())||"error",this._error):r.s6,this._config.text_only?void 0:this._config.title,(0,i.H)({"with-header":!!this._config.title,"text-only":null!==(t=this._config.text_only)&&void 0!==t&&t}),null===(n=this._templateResult)||void 0===n?void 0:n.result):r.s6}updated(e){if(super.updated(e),!this._config||!this.hass)return;e.has("_config")&&this._tryConnect();const t=!!this._templateResult&&!1===this._config.show_empty&&0===this._templateResult.result.length;t!==this.hidden&&(this.style.display=t?"none":"",this.toggleAttribute("hidden",t),(0,d.r)(this,"card-visibility-changed",{value:!t}));const n=e.get("hass"),o=e.get("_config");n&&o&&n.themes===this.hass.themes&&o.theme===this._config.theme||(0,c.Q)(this,this.hass.themes,this._config.theme)}async _tryConnect(){if(void 0===this._unsubRenderTemplate&&this.hass&&this._config){this._error=void 0,this._errorLevel=void 0;try{this._unsubRenderTemplate=(0,h.R)(this.hass.connection,e=>{"error"in e?"ERROR"!==e.level&&"ERROR"===this._errorLevel||(this._error=e.error,this._errorLevel=e.level):this._templateResult=e},{template:this._config.content,entity_ids:this._config.entity_id,variables:{config:this._config,user:this.hass.user.name},strict:!0,report_errors:this.preview}),await this._unsubRenderTemplate}catch(e){this.preview&&(this._error=e.message,this._errorLevel=void 0),this._templateResult={result:this._config.content,listeners:{all:!1,domains:[],entities:[],time:!1}},this._unsubRenderTemplate=void 0}}}async _tryDisconnect(){this._unsubRenderTemplate&&(this._unsubRenderTemplate.then(e=>e()).catch(),this._unsubRenderTemplate=void 0,this._error=void 0,this._errorLevel=void 0)}constructor(...e){super(...e),this.preview=!1}}b.styles=(0,r.AH)(g||(g=f`ha-card{height:100%;overflow-y:auto}ha-alert{margin-bottom:8px}ha-markdown{padding:16px;word-wrap:break-word;text-align:var(--card-text-align,inherit)}.with-header ha-markdown{padding:0 16px 16px}.text-only{background:0 0;box-shadow:none;border:none}.text-only ha-markdown{padding:2px 4px}`)),(0,o.__decorate)([(0,a.MZ)({attribute:!1})],b.prototype,"hass",void 0),(0,o.__decorate)([(0,a.MZ)({type:Boolean})],b.prototype,"preview",void 0),(0,o.__decorate)([(0,a.wk)()],b.prototype,"_config",void 0),(0,o.__decorate)([(0,a.wk)()],b.prototype,"_error",void 0),(0,o.__decorate)([(0,a.wk)()],b.prototype,"_errorLevel",void 0),(0,o.__decorate)([(0,a.wk)()],b.prototype,"_templateResult",void 0),b=(0,o.__decorate)([(0,a.EM)("hui-markdown-card")],b)},996:function(e,t,n){"use strict";n.d(t,{G:function(){return o}});n(23792),n(62953);class o{get(e){return this._cache.get(e)}set(e,t){this._cache.set(e,t),this._expiration&&window.setTimeout(()=>this._cache.delete(e),this._expiration)}has(e){return this._cache.has(e)}constructor(e){this._cache=new Map,this._expiration=e}}},96175:function(e,t,n){var o={"./ha-icon-prev":["89133","61982"],"./ha-icon-button-toolbar":["9882","26431","41983"],"./ha-alert":["38962","19695"],"./ha-icon-button-toggle":["62501","77254"],"./ha-svg-icon.ts":["67094"],"./ha-alert.ts":["38962","19695"],"./ha-icon":["88945","51146"],"./ha-icon-next.ts":["43661","63902"],"./ha-qr-code.ts":["60543","51343","62740"],"./ha-icon-overflow-menu.ts":["75248","46095","26431","22016","17521"],"./ha-icon-button-toggle.ts":["62501","77254"],"./ha-icon-button-group":["39826","13647"],"./ha-svg-icon":["67094"],"./ha-icon-button-prev":["45100","99197"],"./ha-icon-button.ts":["26300"],"./ha-icon-overflow-menu":["75248","46095","26431","22016","17521"],"./ha-icon-button-arrow-next":["99028","54101"],"./ha-icon-button-prev.ts":["45100","99197"],"./ha-icon-picker":["64138","44533","7199","46095","24876","97367","99232"],"./ha-icon-button-toolbar.ts":["9882","26431","41983"],"./ha-icon-button-arrow-prev.ts":["90248","17041"],"./ha-icon-button-next":["3059","81049"],"./ha-icon-next":["43661","63902"],"./ha-icon-picker.ts":["64138","44533","7199","46095","24876","97367","99232"],"./ha-icon-prev.ts":["89133","61982"],"./ha-icon-button-arrow-prev":["90248","17041"],"./ha-icon-button-next.ts":["3059","81049"],"./ha-icon.ts":["88945","51146"],"./ha-qr-code":["60543","51343","62740"],"./ha-icon-button":["26300"],"./ha-icon-button-group.ts":["39826","13647"],"./ha-icon-button-arrow-next.ts":["99028","54101"]};function r(e){if(!n.o(o,e))return Promise.resolve().then(function(){var t=new Error("Cannot find module '"+e+"'");throw t.code="MODULE_NOT_FOUND",t});var t=o[e],r=t[0];return Promise.all(t.slice(1).map(n.e)).then(function(){return n(r)})}r.keys=function(){return Object.keys(o)},r.id=96175,e.exports=r},13611:function(e,t,n){"use strict";var o=n(46518),r=n(22195),a=n(62106),i=n(43724),s=TypeError,l=Object.defineProperty,c=r.self!==r;try{if(i){var d=Object.getOwnPropertyDescriptor(r,"self");!c&&d&&d.get&&d.enumerable||a(r,"self",{get:function(){return r},set:function(e){if(this!==r)throw new s("Illegal invocation");l(r,"self",{value:e,writable:!0,configurable:!0,enumerable:!0})},configurable:!0,enumerable:!0})}else o({global:!0,simple:!0,forced:c},{self:r})}catch(h){}},47075:function(e,t,n){"use strict";n.d(t,{A:function(){return o}});n(89463),n(23792),n(62953);function o(e){return o="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(e){return typeof e}:function(e){return e&&"function"==typeof Symbol&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e},o(e)}},2209:function(e,t,n){"use strict";n.d(t,{LV:function(){return u}});n(89463),n(16280),n(23792),n(72712),n(55081),n(18111),n(61701),n(18237),n(3362),n(84864),n(57465),n(27495),n(62953);const o=Symbol("Comlink.proxy"),r=Symbol("Comlink.endpoint"),a=Symbol("Comlink.releaseProxy"),i=Symbol("Comlink.finalizer"),s=Symbol("Comlink.thrown"),l=e=>"object"==typeof e&&null!==e||"function"==typeof e,c=new Map([["proxy",{canHandle:e=>l(e)&&e[o],serialize(e){const{port1:t,port2:n}=new MessageChannel;return d(e,t),[n,[n]]},deserialize(e){return e.start(),u(e)}}],["throw",{canHandle:e=>l(e)&&s in e,serialize({value:e}){let t;return t=e instanceof Error?{isError:!0,value:{message:e.message,name:e.name,stack:e.stack}}:{isError:!1,value:e},[t,[]]},deserialize(e){if(e.isError)throw Object.assign(new Error(e.value.message),e.value);throw e.value}}]]);function d(e,t=globalThis,n=["*"]){t.addEventListener("message",function r(a){if(!a||!a.data)return;if(!function(e,t){for(const n of e){if(t===n||"*"===n)return!0;if(n instanceof RegExp&&n.test(t))return!0}return!1}(n,a.origin))return void console.warn(`Invalid origin '${a.origin}' for comlink proxy`);const{id:l,type:c,path:u}=Object.assign({path:[]},a.data),p=(a.data.argumentList||[]).map(w);let m;try{const t=u.slice(0,-1).reduce((e,t)=>e[t],e),n=u.reduce((e,t)=>e[t],e);switch(c){case"GET":m=n;break;case"SET":t[u.slice(-1)[0]]=w(a.data.value),m=!0;break;case"APPLY":m=n.apply(t,p);break;case"CONSTRUCT":m=function(e){return Object.assign(e,{[o]:!0})}(new n(...p));break;case"ENDPOINT":{const{port1:t,port2:n}=new MessageChannel;d(e,n),m=function(e,t){return y.set(e,t),e}(t,[t])}break;case"RELEASE":m=void 0;break;default:return}}catch(g){m={value:g,[s]:0}}Promise.resolve(m).catch(e=>({value:e,[s]:0})).then(n=>{const[o,a]=_(n);t.postMessage(Object.assign(Object.assign({},o),{id:l}),a),"RELEASE"===c&&(t.removeEventListener("message",r),h(t),i in e&&"function"==typeof e[i]&&e[i]())}).catch(e=>{const[n,o]=_({value:new TypeError("Unserializable return value"),[s]:0});t.postMessage(Object.assign(Object.assign({},n),{id:l}),o)})}),t.start&&t.start()}function h(e){(function(e){return"MessagePort"===e.constructor.name})(e)&&e.close()}function u(e,t){const n=new Map;return e.addEventListener("message",function(e){const{data:t}=e;if(!t||!t.id)return;const o=n.get(t.id);if(o)try{o(t)}finally{n.delete(t.id)}}),v(e,n,[],t)}function p(e){if(e)throw new Error("Proxy has been released and is not useable")}function m(e){return k(e,new Map,{type:"RELEASE"}).then(()=>{h(e)})}const g=new WeakMap,f="FinalizationRegistry"in globalThis&&new FinalizationRegistry(e=>{const t=(g.get(e)||0)-1;g.set(e,t),0===t&&m(e)});function v(e,t,n=[],o=function(){}){let i=!1;const s=new Proxy(o,{get(o,r){if(p(i),r===a)return()=>{!function(e){f&&f.unregister(e)}(s),m(e),t.clear(),i=!0};if("then"===r){if(0===n.length)return{then:()=>s};const o=k(e,t,{type:"GET",path:n.map(e=>e.toString())}).then(w);return o.then.bind(o)}return v(e,t,[...n,r])},set(o,r,a){p(i);const[s,l]=_(a);return k(e,t,{type:"SET",path:[...n,r].map(e=>e.toString()),value:s},l).then(w)},apply(o,a,s){p(i);const l=n[n.length-1];if(l===r)return k(e,t,{type:"ENDPOINT"}).then(w);if("bind"===l)return v(e,t,n.slice(0,-1));const[c,d]=b(s);return k(e,t,{type:"APPLY",path:n.map(e=>e.toString()),argumentList:c},d).then(w)},construct(o,r){p(i);const[a,s]=b(r);return k(e,t,{type:"CONSTRUCT",path:n.map(e=>e.toString()),argumentList:a},s).then(w)}});return function(e,t){const n=(g.get(t)||0)+1;g.set(t,n),f&&f.register(e,t,e)}(s,e),s}function b(e){const t=e.map(_);return[t.map(e=>e[0]),(n=t.map(e=>e[1]),Array.prototype.concat.apply([],n))];var n}const y=new WeakMap;function _(e){for(const[t,n]of c)if(n.canHandle(e)){const[o,r]=n.serialize(e);return[{type:"HANDLER",name:t,value:o},r]}return[{type:"RAW",value:e},y.get(e)||[]]}function w(e){switch(e.type){case"HANDLER":return c.get(e.name).deserialize(e.value);case"RAW":return e.value}}function k(e,t,n,o){return new Promise(r=>{const a=new Array(4).fill(0).map(()=>Math.floor(Math.random()*Number.MAX_SAFE_INTEGER).toString(16)).join("-");t.set(a,r),e.start&&e.start(),e.postMessage(Object.assign({id:a},n),o)})}}}]);
//# sourceMappingURL=26321.5bd5ddd76b129071.js.map