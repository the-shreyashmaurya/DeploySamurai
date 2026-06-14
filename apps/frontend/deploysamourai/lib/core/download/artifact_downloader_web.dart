import 'dart:html' as html;

Future<void> downloadArtifactUrl(String url) async {
  html.AnchorElement(href: url)
    ..target = '_blank'
    ..download = ''
    ..click();
}
