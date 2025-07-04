/*! Select2 4.1.0-rc.0 | https://github.com/select2/select2/blob/master/LICENSE.md */

(function() {
    if (typeof jQuery === 'undefined') {
        return;
    }

    var $ = jQuery;

    $.fn.select2.amd.define('select2/i18n/ar', [], function() {
        return {
            errorLoading: function() {
                return 'لا يمكن تحميل النتائج';
            },
            inputTooLong: function(args) {
                var overChars = args.input.length - args.maximum;
                
                return 'الرجاء حذف ' + overChars + ' أحرف';
            },
            inputTooShort: function(args) {
                var remainingChars = args.minimum - args.input.length;
                
                return 'الرجاء إدخال ' + remainingChars + ' أحرف أو أكثر';
            },
            loadingMore: function() {
                return 'جاري تحميل نتائج إضافية...';
            },
            maximumSelected: function(args) {
                return 'تستطيع إختيار ' + args.maximum + ' بنود فقط';
            },
            noResults: function() {
                return 'لم يتم العثور على نتائج';
            },
            searching: function() {
                return 'جاري البحث…';
            },
            removeAllItems: function() {
                return 'قم بإزالة كل العناصر';
            },
            removeItem: function() {
                return 'إزالة العنصر';
            },
            search: function() {
                return 'بحث';
            }
        };
    });
})();