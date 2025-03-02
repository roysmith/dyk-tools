"use strict";

const fs = require('node:fs');
const { Pingifier } = require('./dyk_pingifier');
const { mw } = require('mock-mediawiki');
const { describe } = require('node:test');

function getDocument(pathName) {
    return fs.readFileSync(pathName, 'utf8');
}

function loadDocument(pathName) {
    document.documentElement.innerHTML = getDocument(pathName);
}

describe('constructor', () => {

    it('builds an default instance', () => {
        const p = new Pingifier(mw);
        expect(p).toBeInstanceOf(Pingifier);
        expect(p.mw).toBe(mw);
        expect(p.updateTimes).toEqual({});
    });
});

describe('parseLocalUpdateTimes', () => {
    it('finds the preps and queues', () => {
        const html = getDocument('src/js/localUpdateTimes.html');
        const updateTimes = Pingifier.parseLocalUpdateTimes(html);
        expect(updateTimes).toEqual({
            'Queue 1': '17&nbsp;February&nbsp;00:00',
            'Queue 2': '14&nbsp;February&nbsp;00:00',
            'Queue 3': '14&nbsp;February&nbsp;12:00',
            'Queue 4': '15&nbsp;February&nbsp;00:00',
            'Queue 5': '15&nbsp;February&nbsp;12:00',
            'Queue 6': '16&nbsp;February&nbsp;00:00',
            'Queue 7': '16&nbsp;February&nbsp;12:00',
            'Prep 1': '17&nbsp;February&nbsp;00:00',
            'Prep 2': '17&nbsp;February&nbsp;12:00',
            'Prep 3': '18&nbsp;February&nbsp;00:00',
            'Prep 4': '18&nbsp;February&nbsp;12:00',
            'Prep 5': '19&nbsp;February&nbsp;00:00',
            'Prep 6': '16&nbsp;February&nbsp;00:00',
            'Prep 7': '16&nbsp;February&nbsp;12:00',
        });
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
    it('finds a queue', () => {
        document.documentElement.innerHTML = `<body><div>
            <textarea id="dyk-ping-box" rows="8"></textarea>
            </div></body>`;
        let mockApi
        let mockMw = {
        };
        const pingifier = new Pingifier(mockMw);
    })
})
