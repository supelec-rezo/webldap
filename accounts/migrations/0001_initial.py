# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Request'
        db.create_table('accounts_request', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('token', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('uid', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=254)),
            ('firstname', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('lastname', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('expires_at', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('accounts', ['Request'])


    def backwards(self, orm):
        # Deleting model 'Request'
        db.delete_table('accounts_request')


    models = {
        'accounts.request': {
            'Meta': {'object_name': 'Request'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '254'}),
            'expires_at': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'lastname': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'uid': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['accounts']
