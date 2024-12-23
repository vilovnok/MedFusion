import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

@Component({
  selector: 'app-topic-dialog',
  templateUrl: './topic-dialog.component.html',
  styleUrls: ['./topic-dialog.component.scss']
})
export class TopicDialogComponent {
  constructor(@
    Inject(MAT_DIALOG_DATA) public data: { title: string, fullResponse: string },
    private dialogRef: MatDialogRef<TopicDialogComponent> ) {}

  close() {
    this.dialogRef.close();
}
}
