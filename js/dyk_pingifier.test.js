const fs = require('node:fs');
const { Pingifier } = require('./dyk_pingifier');

describe('constructor', () => {

    it('builds an default instance', () => {
        const p = new Pingifier($, mw);
        expect(p).toBeInstanceOf(Pingifier);
        expect(p.$).toBe($);
        expect(p.mw).toBe(mw);
        expect(p.updateTimes).toEqual({});
    });
});

describe('parseLocalUpdateTimes', () => {
    it('finds the preps and queues', () => {
        const html = fs.readFileSync('src/js/localUpdateTimes.html', 'utf8');
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

