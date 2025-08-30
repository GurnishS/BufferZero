import 'package:flutter/material.dart';

import 'add_new_download_task_sheet.dart';
import 'configure_download_task_sheet.dart';

/// Simple facade so callers can open the app's primary bottom modal sheet
/// using `BottomModelSheet.show(context)`. Delegates to
/// `showAddNewDownloadTaskSheet` implemented in
/// `add_new_download_task_sheet.dart`.
class BottomDownloadSheet {
  BottomDownloadSheet._();

  /// Shows the main "Add New Download" bottom sheet.
  static Future<T?> show<T>(BuildContext context) {
    return _showFlow<T>(context);
  }

  static Future<T?> _showFlow<T>(BuildContext context) async {
    // First show the Add New Download sheet. It returns true when the user
    // taps Continue.
    final continuePressed = await showAddNewDownloadTaskSheet<bool>(context);

    if (continuePressed == true) {
      // Open the Configure sheet and return its result.
      return showConfigureDownloadTaskSheet<T>(context);
    }

    return null;
  }
}
