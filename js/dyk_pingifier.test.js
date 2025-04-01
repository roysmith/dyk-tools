"use strict";

const fs = require('node:fs');
const { Pingifier } = require('./dyk_pingifier');
const { describe } = require('node:test');
const { LocalUpdateTimes } = require('./localUpdateTimes');

function getDocument(pathName) {
    return fs.readFileSync(pathName, 'utf8');
}

function loadDocument(pathName) {
    document.documentElement.innerHTML = getDocument(pathName);
}

describe('constructor', () => {
    it('builds a default instance', () => {
        const p = new Pingifier(mw);
        expect(p).toBeInstanceOf(Pingifier);
        expect(p.localUpdateTimes).toBeNull();
    });
});

describe('addPingBox', () => {
    it('adds the l3 header', () => {
        document.documentElement.innerHTML = `
            <body
                <h1 id="firstHeading" class="firstHeading mw-first-heading">
                    <span class="mw-page-title-namespace">Template</span
                    <span class="mw-page-title-separator">:</span>
                    <span class="mw-page-title-main">Did you know nominations/Forbidden City cats</span>
                </h1>
            </body>
            `;

        const pingifier = new Pingifier(mw);
        pingifier.addPingBox();

        expect($('#dyk-ping-box').val())
            .toMatch('===[[Template:Did you know nominations/Forbidden City cats|Forbidden City cats]]===')
    });
});

describe('addPingButtons', () => {
    it('adds the ping buttons', () => {
        loadDocument('src/js/Template:Did_you_know_nominations/Main_Street_Vehicles@1275968747.html');
        const pingifier = new Pingifier(mw);
        pingifier.addPingButtons();
        const $buttons = $(':button.dyk-ping-button');
        expect($.map($buttons, b => $(b).attr('data-username')))
            .toEqual([
                "SL93",
                "Jackdude101",
                "Gatoclass"
            ]);
        expect($('button.dyk-promoter').data('username')).toEqual("SL93")
        expect($('button.dyk-nominator').data('username')).toEqual("Jackdude101")
        expect($('button.dyk-approver').data('username')).toEqual("Gatoclass")
    });
});

describe('classifyUser', () => {
    it('finds the promoter', () => {
        document.documentElement.innerHTML = `<body><p>
            The result was: <b>promoted</b> by <a href="/wiki/User:Foo">Foo</a><br>
            </p></body>`;
        const $anchor = $('a');
        const pingifier = new Pingifier(mw);
        expect(pingifier.classifyUser($anchor)).toEqual("promoter");
    });

    it('finds the nominator', () => {
        document.documentElement.innerHTML = `<body><div>
            5x expanded by <a href="/wiki/User:Epicgenius">Epicgenius</a>
            Number of QPQs required: <b>1</b>. Nominator has 697 past nominations.
            </div></body>`;
        const $anchor = $('a');
        const pingifier = new Pingifier(mw);
        expect(pingifier.classifyUser($anchor)).toEqual("nominator");
    });

    it('finds the approver in a paragraph', () => {
        document.documentElement.innerHTML = `<body><<p>
        <span><a href="/wiki/File:Symbol_confirmed.svg"></a></span>
        Blah
        <a href="/wiki/User:Gatoclass" title="User:Gatoclass">Gatoclass</a>
        </p></body>`;
        const $anchor = $('a');
        const pingifier = new Pingifier(mw);
        expect(pingifier.classifyUser($anchor)).toEqual("approver");
    });

    it('finds the approver in a list item', () => {
        document.documentElement.innerHTML = `<body><li>
        <span><a href="/wiki/File:Symbol_confirmed.svg"></a></span>
        is the best, I think<a href="/wiki/User:DragonflySixtyseven" title="User:DragonflySixtyseven"></a>
        </li></body>`;
        const $anchor = $('a[href*="Dragon"]');
        const pingifier = new Pingifier(mw);
        expect(pingifier.classifyUser($anchor)).toEqual("approver");
    });

    it('finds the approver with voting_keep', () => {
        document.documentElement.innerHTML = `<body><<p>
        <a href="/wiki/File:Symbol_voting_keep.svg"></a>
        Blah
        <a href="/wiki/User:Gatoclass" title="User:Gatoclass">Gatoclass</a>
        </p></body>`;
        const $anchor = $('a');
        const pingifier = new Pingifier(mw);
        expect(pingifier.classifyUser($anchor)).toEqual("approver");
    });

    it('returns null if none of the above', () => {
        document.documentElement.innerHTML = `<body><div>
            <a href="/wiki/User:Epicgenius">Epicgenius</a>
            Whatever.
            </div></body>`;
        const $anchor = $('a');
        const pingifier = new Pingifier(mw);
        expect(pingifier.classifyUser($anchor)).toEqual(null);
    });
});

describe('classifyAllUsers', () => {
    it('builds the map correctly', () => {
        loadDocument('src/js/Template:Did_you_know_nominations/Main_Street_Vehicles@1275968747.html');
        const pingifier = new Pingifier(mw);
        const $userAnchors = pingifier.findUserAnchors();
        const userRoles = pingifier.classifyAllUsers($userAnchors);
        expect(userRoles.get("SL93")).toEqual("promoter");
        expect(userRoles.get("Jackdude101")).toEqual("nominator");
        expect(userRoles.get("Gatoclass")).toEqual("approver");
    });
});

describe('l2Button', () => {
    it('finds a queue', async () => {
        document.documentElement.innerHTML = `
            <body
                <div>
                    <textarea id="dyk-ping-box"></textarea>
                </div>
            </body>
            `;
        const pingifier = new Pingifier(mw);
        pingifier.localUpdateTimes = new LocalUpdateTimes({ 'Queue 1': 'Foo' });
        pingifier.nomination = {
            findHookSet: jest.fn()
                .mockResolvedValue(['Template:Did you know/Queue/1', 'Queue 1'])
        };
        mw.config.get = jest.fn()
            .mockReturnValueOnce('Template:Did you know nominations/Roland L. Bragg')
            .mockReturnValueOnce(79214943);
        mw.Api.prototype.get = jest.fn()
            .mockResolvedValue({
                // Output of https://w.wiki/DQzr
                "batchcomplete": "",
                "query": {
                    "pages": {
                        "79214943": {
                            "pageid": 79214943,
                            "ns": 10,
                            "title": "Template:Did you know nominations/Roland L. Bragg",
                            "linkshere": [
                                {
                                    "pageid": 19951383,
                                    "ns": 10,
                                    "title": "Template:Did you know/Queue/1"
                                }
                            ]
                        }
                    }
                }
            });

        await pingifier.addL2Button();
        await $('#dyk-l2-button').trigger("click");

        expect($('#dyk-ping-box').val()).toMatch('==[[Template:Did you know/Queue/1|Queue 1]] (Foo)==');
    })

    it('finds a prep area', async () => {
        document.documentElement.innerHTML = `
            <body
                <div>
                    <textarea id="dyk-ping-box"></textarea>
                </div>
            </body>
            `;
        const pingifier = new Pingifier(mw);
        pingifier.localUpdateTimes = new LocalUpdateTimes({ 'Prep 1': 'Bar' });
        pingifier.nomination = {
            findHookSet: jest.fn()
                .mockResolvedValue(['Template:Did you know/Preparation area 1', 'Prep 1'])
        };
        mw.config.get = jest.fn()
            .mockReturnValueOnce('Template:Did you know nominations/Blah')
            .mockReturnValueOnce(23001);
        mw.Api.prototype.get = jest.fn()
            .mockResolvedValue({
                "batchcomplete": "",
                "query": {
                    "pages": {
                        "23001": {
                            "pageid": 23001,
                            "ns": 10,
                            "title": "Template:Did you know nominations/Blah",
                            "linkshere": [
                                {
                                    "pageid": 23002,
                                    "ns": 10,
                                    "title": "Template:Did you know/Preparation area 1"
                                }
                            ]
                        }
                    }
                }
            });

        await pingifier.addL2Button();
        await $('#dyk-l2-button').trigger("click");

        expect($('#dyk-ping-box').val()).toMatch('==[[Template:Did you know/Preparation area 1|Prep 1]] (Bar)==');
    })
})
