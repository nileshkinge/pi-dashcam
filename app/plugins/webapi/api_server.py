import logging
import os
from flask import Flask, jsonify, send_from_directory


def create_app(config, segment_manager, health_monitor):
    app = Flask('dashcam_api')
    recordings_path = os.fspath(segment_manager.recordings_path)

    @app.route('/health')
    def health():
        return jsonify(health_monitor.summary())

    @app.route('/status')
    def status():
        return jsonify({
            'recording_path': recordings_path,
            'recordings': [p.name for p in segment_manager.list_segments()],
            'config': config.get('api', {}),
        })

    @app.route('/recordings')
    def recordings():
        return jsonify([p.name for p in segment_manager.list_segments()])

    @app.route('/download/<path:filename>')
    def download(filename):
        return send_from_directory(recordings_path, filename, as_attachment=True)

    return app


class APIServer:
    def __init__(self, config, segment_manager, health_monitor):
        self.config = config
        self.segment_manager = segment_manager
        self.health_monitor = health_monitor
        self.logger = logging.getLogger(self.__class__.__name__)
        self.app = create_app(config, segment_manager, health_monitor)

    def run(self):
        host = self.config['api'].get('host', '0.0.0.0')
        port = int(self.config['api'].get('port', 8080))
        self.logger.info('Starting API server on %s:%s', host, port)
        try:
            self.app.run(host=host, port=port, threaded=True, debug=False)
        except Exception:
            self.logger.exception('Web API server failed')
            self.health_monitor.update_status('api', 'failed')
