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
    it('find the preps and queues', () => {
        const html = fs.readFileSync('src/js/localUpdateTimes.html', 'utf8');
        expect(html).toBeDefined();
    });
});

