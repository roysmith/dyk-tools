"use strict";

const fs = require('node:fs');
const { Pingifier } = require('./dyk_pingifier');
const { mw } = require('mock-mediawiki');

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
        const pingifier = new Pingifier($, mw);
        pingifier.addPingButtons();
        const $buttons = $(':button.dyk-ping-button');
        expect($buttons.length).toEqual(4);
        expect($.map($buttons.prev(), a => $(a).attr('href')))
            .toEqual([
                "/wiki/User:SL93#top",
                "/wiki/User:Jackdude101",
                "/wiki/User:Jackdude101",
                "/wiki/User:Gatoclass",
            ]);
    });
});

