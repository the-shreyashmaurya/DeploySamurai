import 'artifact_downloader_stub.dart'
    if (dart.library.html) 'artifact_downloader_web.dart';

Future<void> downloadArtifact(String url) {
  return downloadArtifactUrl(url);
}
