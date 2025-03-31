"use strict";

const { describe } = require('node:test');
const fs = require('node:fs');

const { Nomination } = require('./nomination');

function getDocument(pathName) {
    return fs.readFileSync(pathName, 'utf8');
}

describe('construct', () => {
    it('generates a document', () => {
        const html = getDocument('src/js/Template:Did_you_know_nominations/Main_Street_Vehicles@1275968747.html');

        const nom = new Nomination('Template:Did you know nominations/Main Street Vehicles', html);

        expect(nom.title).toEqual('Template:Did you know nominations/Main Street Vehicles');
        expect($('h1#firstHeading', nom.document).text())
            .toEqual('Template:Did you know nominations/Main Street Vehicles');
    });
});

describe('build', () => {
    it('builds an instance', async () => {
        $.get = jest.fn()
            .mockResolvedValue(
                getDocument('src/js/Template:Did_you_know_nominations/Main_Street_Vehicles@1275968747.html'));

        const nom = await Nomination.build('Template:Did you know nominations/Foo');

        expect(nom).toBeInstanceOf(Nomination);
        expect($.get).toHaveBeenCalledTimes(1);
        expect($.get).toHaveBeenCalledWith('Template:Did you know nominations/Foo');
        expect($('h1#firstHeading', nom.document).text())
            .toEqual('Template:Did you know nominations/Main Street Vehicles');
    });
});

describe('findHookSet', () => {
    const nom = new Nomination('Template:Did you know nominations/Aliko Dangote',
        '<html></html>');
    it('finds the queue or prep this nomination is part of', async () => {
        mw.Api.prototype.get = jest.fn()
            .mockResolvedValue({
                "batchcomplete": true,
                "query": {
                    "pages": [
                        {
                            "pageid": 79033017,
                            "ns": 10,
                            "title": "Template:Did you know nominations/Aliko Dangote",
                            "linkshere": [
                                {
                                    "pageid": 21870136,
                                    "ns": 10,
                                    "title": "Template:Did you know/Queue/6",
                                    "redirect": false
                                },
                                {
                                    "pageid": 79034641,
                                    "ns": 10,
                                    "title": "Template:Did you know nominations/Cheng Lianzhen",
                                    "redirect": false
                                }
                            ]
                        }
                    ]
                }
            });

        const result = await nom.findHookSet();

        expect(mw.Api.prototype.get).toHaveBeenCalledTimes(1);
        expect(mw.Api.prototype.get).toHaveBeenCalledWith({
            "action": "query",
            "format": "json",
            "prop": "linkshere",
            "titles": "Template:Did you know nominations/Aliko Dangote",
            "formatVersion": 2,
            "lhnamespace": 10,
            "lhlimit": 100,
        });
        expect(result).toEqual([
            "Template:Did you know/Queue/6",
            "Queue 6",
        ]);
    });

    it('returns null if no hookSet', async () => {
        const nom = new Nomination('Template:Did you know nominations/Aliko Dangote',
            '<html></html>');
        mw.Api.prototype.get = jest.fn()
            .mockResolvedValue({
                "batchcomplete": true,
                "query": {
                    "pages": [
                        {
                            "pageid": 79033017,
                            "ns": 10,
                            "title": "Template:Did you know nominations/Aliko Dangote",
                            "linkshere": [
                                {
                                    "pageid": 79034641,
                                    "ns": 10,
                                    "title": "Template:Did you know nominations/Cheng Lianzhen",
                                    "redirect": false
                                }
                            ]
                        }
                    ]
                }
            });

        const result = await nom.findHookSet();

        expect(result).toBeNull();
    });
});

