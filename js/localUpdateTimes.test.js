"use strict";

const { describe } = require('node:test');
const fs = require('node:fs');

const { LocalUpdateTimes } = require('./localUpdateTimes');

function getDocument(pathName) {
    return fs.readFileSync(pathName, 'utf8');
}

describe('constructor', () => {
    it('constructs a default instance', () => {
        const lut = new LocalUpdateTimes();
        expect(lut).toBeInstanceOf(LocalUpdateTimes);
        expect(lut.updateTimes).toBeUndefined();
    });
});

describe('build', () => {
    it('builds the table', async () => {
        $.get = jest.fn()
            .mockResolvedValue(
                getDocument('src/js/localUpdateTimes.html'));

        const lut = await LocalUpdateTimes.build();

        expect($.get)
            .toHaveBeenCalledWith('/wiki/Template:Did_you_know/Queue/LocalUpdateTimes');
        expect(lut.updateTimes).toEqual({
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
})

describe('parseLocalUpdateTimes', () => {
    it('finds the preps and queues', () => {
        const html = getDocument('src/js/localUpdateTimes.html');
        const updateTimes = LocalUpdateTimes.parse(html);
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
