#import <Foundation/Foundation.h>

#ifdef __cplusplus
extern "C" {
#endif

// Returns the translation of `key` for the active language.
// The English text itself is the key; when no translation exists the key is returned unchanged,
// so untranslated strings simply show up in English. See TRANSLATING.md.
NSString *YTLPLocalizedString(NSString *key) __attribute__((format_arg(1)));

#ifdef __cplusplus
}
#endif
