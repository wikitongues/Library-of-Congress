#!/usr/bin/env node

'use strict';
var Airtable = require('airtable');
var fs = require('fs');
var destination = process.argv[3]

var single = process.argv[2];

var fields = [
  'Identifier',
  'Title',
  'Creator',
  'Description',
  'Subject [Language: Genealogy]',
  'Subject [Language: Continent of Origin]',
  'Subject [Language: Nation of Origin]',
  'Subject [Speaker Genders]',
  'Creator [Speakers]',
  'Creator [Caption Authors]',
  'Creator [Videographer]',
  'Creator [Facilitator]',
  'Date Created',
  'Type',
  'Format',
  'Language [Speaker preferred name]',
  'Language [ISO Code 639-3]',
  'Language [Ethnologue Name]',
  'Language [Glottocode]',
  'Language [Dialect Glottocode]',
  'Language [Macro: ISO Code 639-3]',
  'Caption [Language: Ethnologue name]',
  'Caption [Language: ISO Code 639-3]',
  'Caption [Language: Glottocode]',
  'Caption [File: Identifier]',
  'Caption [File: Link]',
  'Coverage [Video Nation]',
  'Coverage [Video Territory]',
  'Coverage [Distribution]',
  'Rights',
  'Publisher',
  'Date Received',
  'Encoded Data',
  'Tagged Data',
  'Duration',
  'Format [Type]',
  'Format [Profile]',
  'Codec ID',
  'File size',
  'Format [Info]',
  'Format [Settings]',
  'Format [Settings: CABAC]',
  'Format [Settings: ReFrames]',
  'Codec ID/Info',
  'Bit rate',
  'Width',
  'Height',
  'Display Aspect Ratio',
  'Frame Rate',
  'Standard',
  'Color Space',
  'Chroma Subsampling',
  'Bit Depth',
  'Scan Type',
  'Bits (Pixel*Frame)',
  'Stream size',
  'Color range',
  'Color primaries',
  'Transfer characteristics',
  'Matrix coefficients',
  'Codec configuration box',
  'Format audio',
  'Format/Info Audio',
  'Bit Rate Audio',
  'Bit rate mode audio',
  'Codec ID Audio',
  'Channel(s)',
  'Channel layout',
  'Compression mode',
  'Sampling rate',
  'Stream size audio',
  'Reference ID [Ethnologue]',
  'Editing Status'
];

try {
  var base = new Airtable({apiKey: process.env.APIKEY}).base(process.env.BASE);

  var identifier = single.replace(/\+/g, '-');

  base('Oral Histories').select({
      view: "Public Archival View",
      cellFormat: "string",
      timeZone: "America/New_York",
      userLocale: "en-ca",
      filterByFormula: "Identifier='"+identifier+"'",
      fields
  }).eachPage(function page(records, fetchNextPage) {
    if (!Array.isArray(records) || !!records.length) {
      records.forEach(function(record) {
          const content = [
            `Metadata for ${record.get('Identifier')}`,

            ...fields.map(field => `${field}: ${record.get(field)}`)
          ].join('\n') + '\r\n';

          fs.writeFileSync(`${destination}/loctemp__${single}/${single}__metadata.txt`, content);
      });
      fetchNextPage();
    } else {
      console.log(`\x1b[31mWarning! ID '${identifier}' not found on airtable.`);
      return process.exit(1);
    }
  }, function done(err) {
      if (err) {
        console.error(err);
        return process.exit(1);
      }
  });
} catch (e) {
  console.error(e);
  return process.exit(1);
}
