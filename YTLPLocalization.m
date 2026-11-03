#import "YTLPLocalization.h"

// Translations are compiled into the dylib (a sideloaded tweak has no resource bundle).
// tools/translations.py generates this header from Localization/*.strings at build time.
#if __has_include("YTLPTranslations.generated.h")
#import "YTLPTranslations.generated.h"
#endif
#ifndef YTLP_TRANSLATION_COUNT
#define YTLP_TRANSLATION_COUNT 0
#endif

#if YTLP_TRANSLATION_COUNT > 0

static NSString *ytlp_normalizedLanguageTag(NSString *tag) {
    return [[tag stringByReplacingOccurrencesOfString:@"_" withString:@"-"] lowercaseString];
}

static NSDictionary<NSString *, NSString *> *ytlp_parseTranslation(int index) {
    NSString *text = [NSString stringWithUTF8String:ytlp_translation_texts[index]];
    if (text.length == 0) return nil;
    NSDictionary *parsed = nil;
    @try { parsed = [text propertyListFromStringsFileFormat]; } @catch (__unused NSException *e) {}
    return [parsed isKindOfClass:[NSDictionary class]] ? parsed : nil;
}

static NSDictionary<NSString *, NSString *> *ytlp_loadTable(void) {
    NSMutableDictionary<NSString *, NSNumber *> *indexByCode = [NSMutableDictionary dictionary];
    for (int i = 0; i < YTLP_TRANSLATION_COUNT; i++) {
        NSString *code = [NSString stringWithUTF8String:ytlp_translation_codes[i]];
        if (code.length > 0) indexByCode[ytlp_normalizedLanguageTag(code)] = @(i);
    }

    // Candidates in priority order: explicit override, the language the app itself runs in,
    // then the system language list.
    NSMutableArray<NSString *> *candidates = [NSMutableArray array];
    NSString *override = [[NSUserDefaults standardUserDefaults] stringForKey:@"ytlp_language"];
    if (override.length > 0 && ![override isEqualToString:@"auto"]) [candidates addObject:override];
    [candidates addObjectsFromArray:[[NSBundle mainBundle] preferredLocalizations] ?: @[]];
    [candidates addObjectsFromArray:[NSLocale preferredLanguages] ?: @[]];

    for (NSString *candidate in candidates) {
        NSString *tag = ytlp_normalizedLanguageTag(candidate);
        // English is the source language: nothing to translate
        if ([tag isEqualToString:@"en"] || [tag hasPrefix:@"en-"]) return @{};

        // pt-br-xx -> pt-br -> pt
        while (tag.length > 0) {
            NSNumber *idx = indexByCode[tag];
            if (idx) {
                NSDictionary *table = ytlp_parseTranslation(idx.intValue);
                if (table) return table;
            }
            NSRange dash = [tag rangeOfString:@"-" options:NSBackwardsSearch];
            if (dash.location == NSNotFound) break;
            tag = [tag substringToIndex:dash.location];
        }
    }
    return @{};
}

#endif // YTLP_TRANSLATION_COUNT > 0

NSString *YTLPLocalizedString(NSString *key) {
    if (key.length == 0) return key;
#if YTLP_TRANSLATION_COUNT > 0
    static NSDictionary<NSString *, NSString *> *table = nil;
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{ table = ytlp_loadTable(); });
    NSString *value = table[key];
    if ([value isKindOfClass:[NSString class]] && value.length > 0) return value;
#endif
    return key;
}
