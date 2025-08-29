import 'package:flutter/material.dart';

import 'add_new_download_task_sheet.dart';

/// Simple facade so callers can open the app's primary bottom modal sheet
/// using `BottomModelSheet.show(context)`. Delegates to
/// `showAddNewDownloadTaskSheet` implemented in
/// `add_new_download_task_sheet.dart`.
class BottomDownloadSheet {
  BottomDownloadSheet._();

  /// Shows the main "Add New Download" bottom sheet.
  static Future<T?> show<T>(BuildContext context) {
    return showAddNewDownloadTaskSheet<T>(context);
  }
}
